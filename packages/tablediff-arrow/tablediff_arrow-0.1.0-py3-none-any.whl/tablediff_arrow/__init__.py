"""
tablediff-arrow: Fast, file-based diffs for Parquet/CSV/Arrow data.
"""

__version__ = "0.1.0"

from .compare import DiffResult, TableDiff

__all__ = ["TableDiff", "DiffResult", "__version__"]
