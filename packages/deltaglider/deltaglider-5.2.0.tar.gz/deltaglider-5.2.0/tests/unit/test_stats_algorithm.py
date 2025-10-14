"""Exhaustive tests for the bucket statistics algorithm."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from deltaglider.client_operations.stats import get_bucket_stats


class TestBucketStatsAlgorithm:
    """Test suite for get_bucket_stats algorithm."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock DeltaGliderClient."""
        client = Mock()
        client.service = Mock()
        client.service.storage = Mock()
        client.service.logger = Mock()
        return client

    def test_empty_bucket(self, mock_client):
        """Test statistics for an empty bucket."""
        # Setup: Empty bucket
        mock_client.service.storage.list_objects.return_value = {
            "objects": [],
            "is_truncated": False,
        }

        # Execute
        stats = get_bucket_stats(mock_client, "empty-bucket")

        # Verify
        assert stats.bucket == "empty-bucket"
        assert stats.object_count == 0
        assert stats.total_size == 0
        assert stats.compressed_size == 0
        assert stats.space_saved == 0
        assert stats.average_compression_ratio == 0.0
        assert stats.delta_objects == 0
        assert stats.direct_objects == 0

    def test_bucket_with_only_direct_files(self, mock_client):
        """Test bucket with only direct files (no compression)."""
        # Setup: Bucket with 3 direct files
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "file1.pdf", "size": 1000000, "last_modified": "2024-01-01"},
                {"key": "file2.html", "size": 500000, "last_modified": "2024-01-02"},
                {"key": "file3.txt", "size": 250000, "last_modified": "2024-01-03"},
            ],
            "is_truncated": False,
        }
        mock_client.service.storage.head.return_value = None

        # Execute
        stats = get_bucket_stats(mock_client, "direct-only-bucket")

        # Verify
        assert stats.object_count == 3
        assert stats.total_size == 1750000  # Sum of all files
        assert stats.compressed_size == 1750000  # Same as total (no compression)
        assert stats.space_saved == 0
        assert stats.average_compression_ratio == 0.0
        assert stats.delta_objects == 0
        assert stats.direct_objects == 3

    def test_bucket_with_delta_compression(self, mock_client):
        """Test bucket with delta-compressed files."""
        # Setup: Bucket with reference.bin and 2 delta files
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {"key": "file1.zip.delta", "size": 50000, "last_modified": "2024-01-02"},
                {"key": "file2.zip.delta", "size": 60000, "last_modified": "2024-01-03"},
            ],
            "is_truncated": False,
        }

        # Mock metadata for delta files
        def mock_head(path):
            if "file1.zip.delta" in path:
                head = Mock()
                head.metadata = {"file_size": "19500000", "compression_ratio": "0.997"}
                return head
            elif "file2.zip.delta" in path:
                head = Mock()
                head.metadata = {"file_size": "19600000", "compression_ratio": "0.997"}
                return head
            return None

        mock_client.service.storage.head.side_effect = mock_head

        # Execute
        stats = get_bucket_stats(mock_client, "compressed-bucket")

        # Verify
        assert stats.object_count == 2  # Only delta files counted (not reference.bin)
        assert stats.total_size == 39100000  # 19.5M + 19.6M
        assert stats.compressed_size == 20110000  # reference (20M) + deltas (50K + 60K)
        assert stats.space_saved == 18990000  # ~19MB saved
        assert stats.average_compression_ratio > 0.48  # ~48.6% compression
        assert stats.delta_objects == 2
        assert stats.direct_objects == 0

    def test_orphaned_reference_bin_detection(self, mock_client):
        """Test detection of orphaned reference.bin files."""
        # Setup: Bucket with reference.bin but no delta files
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {"key": "regular.pdf", "size": 1000000, "last_modified": "2024-01-02"},
            ],
            "is_truncated": False,
        }
        mock_client.service.storage.head.return_value = None

        # Execute
        stats = get_bucket_stats(mock_client, "orphaned-ref-bucket")

        # Verify stats
        assert stats.object_count == 1  # Only regular.pdf
        assert stats.total_size == 1000000  # Only regular.pdf size
        assert stats.compressed_size == 1000000  # reference.bin NOT included
        assert stats.space_saved == 0
        assert stats.delta_objects == 0
        assert stats.direct_objects == 1

        # Verify warning was logged
        warning_calls = mock_client.service.logger.warning.call_args_list
        assert any("ORPHANED REFERENCE FILE" in str(call) for call in warning_calls)
        assert any("20,000,000 bytes" in str(call) for call in warning_calls)
        assert any(
            "aws s3 rm s3://orphaned-ref-bucket/reference.bin" in str(call)
            for call in warning_calls
        )

    def test_mixed_bucket(self, mock_client):
        """Test bucket with both delta and direct files."""
        # Setup: Mixed bucket
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "pro/reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {"key": "pro/v1.zip.delta", "size": 50000, "last_modified": "2024-01-02"},
                {"key": "pro/v2.zip.delta", "size": 60000, "last_modified": "2024-01-03"},
                {"key": "docs/readme.pdf", "size": 500000, "last_modified": "2024-01-04"},
                {"key": "docs/manual.html", "size": 300000, "last_modified": "2024-01-05"},
            ],
            "is_truncated": False,
        }

        # Mock metadata for delta files
        def mock_head(path):
            if "v1.zip.delta" in path:
                head = Mock()
                head.metadata = {"file_size": "19500000"}
                return head
            elif "v2.zip.delta" in path:
                head = Mock()
                head.metadata = {"file_size": "19600000"}
                return head
            return None

        mock_client.service.storage.head.side_effect = mock_head

        # Execute
        stats = get_bucket_stats(mock_client, "mixed-bucket")

        # Verify
        assert stats.object_count == 4  # 2 delta + 2 direct files
        assert stats.total_size == 39900000  # 19.5M + 19.6M + 0.5M + 0.3M
        assert stats.compressed_size == 20910000  # ref (20M) + deltas (110K) + direct (800K)
        assert stats.space_saved == 18990000
        assert stats.delta_objects == 2
        assert stats.direct_objects == 2

    def test_sha1_files_included(self, mock_client):
        """Test that .sha1 checksum files are counted properly."""
        # Setup: Bucket with .sha1 files
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "file1.zip", "size": 1000000, "last_modified": "2024-01-01"},
                {"key": "file1.zip.sha1", "size": 41, "last_modified": "2024-01-01"},
                {"key": "file2.tar", "size": 2000000, "last_modified": "2024-01-02"},
                {"key": "file2.tar.sha1", "size": 41, "last_modified": "2024-01-02"},
            ],
            "is_truncated": False,
        }
        mock_client.service.storage.head.return_value = None

        # Execute
        stats = get_bucket_stats(mock_client, "sha1-bucket")

        # Verify - .sha1 files ARE counted
        assert stats.object_count == 4
        assert stats.total_size == 3000082  # All files including .sha1
        assert stats.compressed_size == 3000082
        assert stats.direct_objects == 4

    def test_multiple_deltaspaces(self, mock_client):
        """Test bucket with multiple deltaspaces (different prefixes)."""
        # Setup: Multiple deltaspaces
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "pro/reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {"key": "pro/v1.zip.delta", "size": 50000, "last_modified": "2024-01-02"},
                {
                    "key": "enterprise/reference.bin",
                    "size": 25000000,
                    "last_modified": "2024-01-03",
                },
                {"key": "enterprise/v1.zip.delta", "size": 70000, "last_modified": "2024-01-04"},
            ],
            "is_truncated": False,
        }

        # Mock metadata
        def mock_head(path):
            if "pro/v1.zip.delta" in path:
                head = Mock()
                head.metadata = {"file_size": "19500000"}
                return head
            elif "enterprise/v1.zip.delta" in path:
                head = Mock()
                head.metadata = {"file_size": "24500000"}
                return head
            return None

        mock_client.service.storage.head.side_effect = mock_head

        # Execute
        stats = get_bucket_stats(mock_client, "multi-deltaspace-bucket")

        # Verify
        assert stats.object_count == 2  # Only delta files
        assert stats.total_size == 44000000  # 19.5M + 24.5M
        assert stats.compressed_size == 45120000  # Both references + both deltas
        assert stats.delta_objects == 2
        assert stats.direct_objects == 0

    def test_pagination_handling(self, mock_client):
        """Test handling of paginated results."""
        # Setup: Paginated responses
        mock_client.service.storage.list_objects.side_effect = [
            {
                "objects": [
                    {"key": f"file{i}.txt", "size": 1000, "last_modified": "2024-01-01"}
                    for i in range(1000)
                ],
                "is_truncated": True,
                "next_continuation_token": "token1",
            },
            {
                "objects": [
                    {"key": f"file{i}.txt", "size": 1000, "last_modified": "2024-01-01"}
                    for i in range(1000, 1500)
                ],
                "is_truncated": False,
            },
        ]
        mock_client.service.storage.head.return_value = None

        # Execute
        stats = get_bucket_stats(mock_client, "paginated-bucket")

        # Verify
        assert stats.object_count == 1500
        assert stats.total_size == 1500000
        assert stats.compressed_size == 1500000
        assert stats.direct_objects == 1500

        # Verify pagination was handled
        assert mock_client.service.storage.list_objects.call_count == 2

    def test_delta_file_without_metadata(self, mock_client):
        """Test handling of delta files with missing metadata."""
        # Setup: Delta file without metadata
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {"key": "file.zip.delta", "size": 50000, "last_modified": "2024-01-02"},
            ],
            "is_truncated": False,
        }

        # No metadata available
        mock_client.service.storage.head.return_value = None

        # Execute
        stats = get_bucket_stats(mock_client, "no-metadata-bucket")

        # Verify - falls back to using delta size as original size
        assert stats.object_count == 1
        assert stats.total_size == 50000  # Falls back to delta size
        assert stats.compressed_size == 20050000  # reference + delta
        assert stats.delta_objects == 1

        # Verify warning was logged
        warning_calls = mock_client.service.logger.warning.call_args_list
        assert any("no original_size" in str(call) for call in warning_calls)

    def test_parallel_metadata_fetching(self, mock_client):
        """Test that metadata is fetched in parallel for performance."""
        # Setup: Many delta files
        num_deltas = 50
        objects = [{"key": "reference.bin", "size": 20000000, "last_modified": "2024-01-01"}]
        objects.extend(
            [
                {
                    "key": f"file{i}.zip.delta",
                    "size": 50000 + i,
                    "last_modified": f"2024-01-{i + 2:02d}",
                }
                for i in range(num_deltas)
            ]
        )

        mock_client.service.storage.list_objects.return_value = {
            "objects": objects,
            "is_truncated": False,
        }

        # Mock metadata
        def mock_head(path):
            head = Mock()
            head.metadata = {"file_size": "19500000"}
            return head

        mock_client.service.storage.head.side_effect = mock_head

        # Execute with mocked ThreadPoolExecutor
        with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
            mock_pool = MagicMock()
            mock_executor.return_value.__enter__.return_value = mock_pool

            # Simulate parallel execution
            futures = []
            for i in range(num_deltas):
                future = Mock()
                future.result.return_value = (f"file{i}.zip.delta", {"file_size": "19500000"})
                futures.append(future)

            mock_pool.submit.side_effect = futures
            patch_as_completed = patch(
                "concurrent.futures.as_completed",
                return_value=futures,
            )

            with patch_as_completed:
                _ = get_bucket_stats(mock_client, "parallel-bucket")

        # Verify ThreadPoolExecutor was used with correct max_workers
        mock_executor.assert_called_once_with(max_workers=10)  # min(10, 50) = 10

    def test_detailed_stats_flag(self, mock_client):
        """Test that detailed_stats flag controls metadata fetching."""
        # Setup
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {"key": "file.zip.delta", "size": 50000, "last_modified": "2024-01-02"},
            ],
            "is_truncated": False,
        }

        # Test with detailed_stats=False (default)
        # NOTE: Currently, the implementation always fetches metadata regardless of the flag
        # This test documents the current behavior
        _ = get_bucket_stats(mock_client, "test-bucket", detailed_stats=False)

        # Currently metadata is always fetched for delta files
        assert mock_client.service.storage.head.called

        # Reset mock
        mock_client.service.storage.head.reset_mock()

        # Test with detailed_stats=True
        mock_client.service.storage.head.return_value = Mock(metadata={"file_size": "19500000"})

        _ = get_bucket_stats(mock_client, "test-bucket", detailed_stats=True)

        # Should fetch metadata
        assert mock_client.service.storage.head.called

    def test_error_handling_in_metadata_fetch(self, mock_client):
        """Test graceful handling of errors during metadata fetch."""
        # Setup
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {"key": "file1.zip.delta", "size": 50000, "last_modified": "2024-01-02"},
                {"key": "file2.zip.delta", "size": 60000, "last_modified": "2024-01-03"},
            ],
            "is_truncated": False,
        }

        # Mock metadata fetch to fail for one file
        def mock_head(path):
            if "file1.zip.delta" in path:
                raise Exception("S3 error")
            elif "file2.zip.delta" in path:
                head = Mock()
                head.metadata = {"file_size": "19600000"}
                return head
            return None

        mock_client.service.storage.head.side_effect = mock_head

        # Execute - should handle error gracefully
        stats = get_bucket_stats(mock_client, "error-bucket", detailed_stats=True)

        # Verify - file1 uses fallback, file2 uses metadata
        assert stats.object_count == 2
        assert stats.delta_objects == 2
        # file1 falls back to delta size (50000), file2 uses metadata (19600000)
        assert stats.total_size == 50000 + 19600000

    def test_multiple_orphaned_references(self, mock_client):
        """Test detection of multiple orphaned reference.bin files."""
        # Setup: Multiple orphaned references
        mock_client.service.storage.list_objects.return_value = {
            "objects": [
                {"key": "pro/reference.bin", "size": 20000000, "last_modified": "2024-01-01"},
                {
                    "key": "enterprise/reference.bin",
                    "size": 25000000,
                    "last_modified": "2024-01-02",
                },
                {"key": "community/reference.bin", "size": 15000000, "last_modified": "2024-01-03"},
                {"key": "regular.pdf", "size": 1000000, "last_modified": "2024-01-04"},
            ],
            "is_truncated": False,
        }
        mock_client.service.storage.head.return_value = None

        # Execute
        stats = get_bucket_stats(mock_client, "multi-orphaned-bucket")

        # Verify stats
        assert stats.object_count == 1  # Only regular.pdf
        assert stats.total_size == 1000000
        assert stats.compressed_size == 1000000  # No references included
        assert stats.space_saved == 0

        # Verify warnings for all orphaned references
        warning_calls = [str(call) for call in mock_client.service.logger.warning.call_args_list]
        warning_text = " ".join(warning_calls)

        assert "ORPHANED REFERENCE FILE" in warning_text
        assert "3 reference.bin file(s)" in warning_text
        assert "60,000,000 bytes" in warning_text  # Total of all references
        assert "s3://multi-orphaned-bucket/pro/reference.bin" in warning_text
        assert "s3://multi-orphaned-bucket/enterprise/reference.bin" in warning_text
        assert "s3://multi-orphaned-bucket/community/reference.bin" in warning_text
