"""
Data loading module for reading Parquet, CSV, and Arrow files from local or S3.
"""

from pathlib import Path

import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq


def load_table(path: str | Path, file_format: str | None = None, filesystem=None) -> pa.Table:
    """
    Load a table from a file path (local or S3).

    Args:
        path: Path to the file (local path or S3 URI like s3://bucket/key)
        file_format: File format ('parquet', 'csv', 'arrow'). If None, inferred from extension.
        filesystem: Optional filesystem object (e.g., s3fs for S3 access)

    Returns:
        PyArrow Table
    """
    path_str = str(path)

    # Infer format from extension if not provided
    if file_format is None:
        if path_str.endswith(".parquet") or path_str.endswith(".pq"):
            file_format = "parquet"
        elif path_str.endswith(".csv"):
            file_format = "csv"
        elif path_str.endswith(".arrow") or path_str.endswith(".feather"):
            file_format = "arrow"
        else:
            raise ValueError(f"Cannot infer file format from path: {path_str}")

    # Handle S3 paths
    if path_str.startswith("s3://"):
        if filesystem is None:
            try:
                import s3fs

                filesystem = s3fs.S3FileSystem()
            except ImportError as err:
                raise ImportError(
                    "s3fs is required for S3 access. Install with: pip install tablediff-arrow[s3]"
                ) from err

    # Load based on format
    if file_format == "parquet":
        return pq.read_table(path_str, filesystem=filesystem)
    elif file_format == "csv":
        if filesystem:
            with filesystem.open(path_str, "rb") as f:
                return csv.read_csv(f)
        else:
            return csv.read_csv(path_str)
    elif file_format == "arrow":
        if filesystem:
            with filesystem.open(path_str, "rb") as f:
                with pa.ipc.open_file(f) as reader:
                    return reader.read_all()
        else:
            with pa.ipc.open_file(path_str) as reader:
                return reader.read_all()
    else:
        raise ValueError(f"Unsupported file format: {file_format}")
