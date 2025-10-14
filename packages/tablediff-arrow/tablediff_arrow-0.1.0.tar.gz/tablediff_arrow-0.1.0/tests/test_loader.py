"""
Tests for the loader module.
"""

import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq
import pytest

from tablediff_arrow.loader import load_table


@pytest.fixture
def sample_table():
    """Create a sample PyArrow table for testing."""
    return pa.table(
        {
            "id": [1, 2, 3, 4],
            "name": ["Alice", "Bob", "Charlie", "David"],
            "value": [10.5, 20.3, 30.7, 40.1],
        }
    )


def test_load_parquet(sample_table):
    """Test loading a Parquet file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.parquet"
        pq.write_table(sample_table, path)

        loaded = load_table(path)
        assert loaded.equals(sample_table)


def test_load_parquet_explicit_format(sample_table):
    """Test loading a Parquet file with explicit format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.pq"
        pq.write_table(sample_table, path)

        loaded = load_table(path, file_format="parquet")
        assert loaded.equals(sample_table)


def test_load_csv(sample_table):
    """Test loading a CSV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.csv"
        csv.write_csv(sample_table, path)

        loaded = load_table(path)
        # CSV doesn't preserve exact types, so compare as pandas
        assert loaded.to_pandas().equals(sample_table.to_pandas())


def test_load_arrow(sample_table):
    """Test loading an Arrow IPC file."""
    import os
    import tempfile

    fd, temp_path = tempfile.mkstemp(suffix=".arrow")
    os.close(fd)  # Close the file descriptor immediately

    try:
        with pa.ipc.new_file(temp_path, sample_table.schema) as writer:
            writer.write_table(sample_table)

        loaded = load_table(temp_path)
        assert loaded.equals(sample_table)
    finally:
        # Clean up manually
        try:
            os.unlink(temp_path)
        except (OSError, PermissionError):
            pass  # Ignore cleanup errors


def test_load_feather(sample_table):
    """Test loading a Feather file (Arrow IPC format)."""
    import os
    import tempfile

    fd, temp_path = tempfile.mkstemp(suffix=".feather")
    os.close(fd)  # Close the file descriptor immediately

    try:
        with pa.ipc.new_file(temp_path, sample_table.schema) as writer:
            writer.write_table(sample_table)

        loaded = load_table(temp_path)
        assert loaded.equals(sample_table)
    finally:
        # Clean up manually
        try:
            os.unlink(temp_path)
        except (OSError, PermissionError):
            pass  # Ignore cleanup errors


def test_invalid_format():
    """Test that invalid format raises an error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.unknown"

        with pytest.raises(ValueError, match="Cannot infer file format"):
            load_table(path)


def test_unsupported_format(sample_table):
    """Test that unsupported format raises an error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.parquet"
        pq.write_table(sample_table, path)

        with pytest.raises(ValueError, match="Unsupported file format"):
            load_table(path, file_format="json")
