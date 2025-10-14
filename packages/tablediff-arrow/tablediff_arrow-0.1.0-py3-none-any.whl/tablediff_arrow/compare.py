"""
Core comparison logic for table diffs with keyed comparisons and numeric tolerances.
"""

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pyarrow as pa

from .loader import load_table


@dataclass
class DiffResult:
    """Result of a table comparison."""

    matched_rows: int = 0
    left_only_rows: int = 0
    right_only_rows: int = 0
    changed_rows: int = 0
    total_changes: int = 0
    column_changes: dict[str, int] = field(default_factory=dict)
    differences: pa.Table | None = None
    left_only: pa.Table | None = None
    right_only: pa.Table | None = None

    @property
    def has_differences(self) -> bool:
        """Check if there are any differences."""
        return self.left_only_rows > 0 or self.right_only_rows > 0 or self.changed_rows > 0

    def summary(self) -> str:
        """Return a summary string of the comparison."""
        lines = [
            "Table Comparison Summary:",
            f"  Matched rows: {self.matched_rows}",
            f"  Changed rows: {self.changed_rows}",
            f"  Left-only rows: {self.left_only_rows}",
            f"  Right-only rows: {self.right_only_rows}",
            f"  Total changes: {self.total_changes}",
        ]
        if self.column_changes:
            lines.append("  Changes by column:")
            for col, count in sorted(self.column_changes.items()):
                lines.append(f"    {col}: {count}")
        return "\n".join(lines)


class TableDiff:
    """
    Compare two tables with keyed comparisons and numeric tolerances.
    """

    def __init__(
        self,
        key_columns: list[str],
        tolerance: dict[str, float] | None = None,
        relative_tolerance: dict[str, float] | None = None,
    ):
        """
        Initialize TableDiff.

        Args:
            key_columns: List of column names to use as the join key
            tolerance: Absolute tolerance per column for numeric comparisons
            relative_tolerance: Relative tolerance per column for numeric comparisons
        """
        self.key_columns = key_columns
        self.tolerance = tolerance or {}
        self.relative_tolerance = relative_tolerance or {}

    def compare_files(
        self,
        left_path: str | Path,
        right_path: str | Path,
        left_format: str | None = None,
        right_format: str | None = None,
        filesystem=None,
    ) -> DiffResult:
        """
        Compare two files.

        Args:
            left_path: Path to the left/source file
            right_path: Path to the right/target file
            left_format: Format of left file (inferred if None)
            right_format: Format of right file (inferred if None)
            filesystem: Optional filesystem for S3 access

        Returns:
            DiffResult object
        """
        left_table = load_table(left_path, left_format, filesystem)
        right_table = load_table(right_path, right_format, filesystem)
        return self.compare_tables(left_table, right_table)

    def compare_tables(
        self,
        left: pa.Table,
        right: pa.Table,
    ) -> DiffResult:
        """
        Compare two PyArrow tables.

        Args:
            left: Left/source table
            right: Right/target table

        Returns:
            DiffResult object
        """
        # Convert to pandas for easier comparison
        left_df = left.to_pandas()
        right_df = right.to_pandas()

        # Validate key columns exist
        for col in self.key_columns:
            if col not in left_df.columns:
                raise ValueError(f"Key column '{col}' not found in left table")
            if col not in right_df.columns:
                raise ValueError(f"Key column '{col}' not found in right table")

        # Set index on key columns for comparison
        left_df = left_df.set_index(self.key_columns)
        right_df = right_df.set_index(self.key_columns)

        # Find rows only in left, only in right, and in both
        left_only_idx = left_df.index.difference(right_df.index)
        right_only_idx = right_df.index.difference(left_df.index)
        common_idx = left_df.index.intersection(right_df.index)

        result = DiffResult()
        result.left_only_rows = len(left_only_idx)
        result.right_only_rows = len(right_only_idx)

        # Store left-only and right-only rows
        if len(left_only_idx) > 0:
            result.left_only = pa.Table.from_pandas(left_df.loc[left_only_idx].reset_index())
        if len(right_only_idx) > 0:
            result.right_only = pa.Table.from_pandas(right_df.loc[right_only_idx].reset_index())

        # Compare common rows
        if len(common_idx) > 0:
            left_common = left_df.loc[common_idx]
            right_common = right_df.loc[common_idx]

            # Compare each column
            diff_rows = []
            column_changes = {}

            for col in left_common.columns:
                if col not in right_common.columns:
                    continue

                left_col = left_common[col]
                right_col = right_common[col]

                # Apply tolerance for numeric columns
                if pd.api.types.is_numeric_dtype(left_col):
                    abs_tol = self.tolerance.get(col, 0.0)
                    rel_tol = self.relative_tolerance.get(col, 0.0)

                    if rel_tol > 0:
                        # Relative tolerance
                        diff_mask = ~pd.isna(left_col) & ~pd.isna(right_col)
                        if diff_mask.any():
                            rel_diff = (left_col - right_col).abs() / right_col.abs()
                            diff_mask = diff_mask & (rel_diff > rel_tol)
                    elif abs_tol > 0:
                        # Absolute tolerance
                        diff_mask = (left_col - right_col).abs() > abs_tol
                    else:
                        # No tolerance
                        diff_mask = left_col != right_col
                        # Handle NaN comparisons
                        diff_mask = diff_mask & ~(pd.isna(left_col) & pd.isna(right_col))
                else:
                    # Non-numeric comparison
                    diff_mask = left_col != right_col
                    # Handle NaN/None comparisons
                    diff_mask = diff_mask & ~(pd.isna(left_col) & pd.isna(right_col))

                num_changes = diff_mask.sum()
                if num_changes > 0:
                    column_changes[col] = int(num_changes)

                    # Record differences
                    for idx in diff_mask[diff_mask].index:
                        diff_rows.append(
                            {
                                **{
                                    k: idx[i] if isinstance(idx, tuple) else idx
                                    for i, k in enumerate(self.key_columns)
                                },
                                "column": col,
                                "left_value": left_col.loc[idx],
                                "right_value": right_col.loc[idx],
                            }
                        )

            result.column_changes = column_changes
            result.total_changes = sum(column_changes.values())
            result.changed_rows = len(set(tuple(d[k] for k in self.key_columns) for d in diff_rows))
            result.matched_rows = len(common_idx) - result.changed_rows

            # Create differences table
            if diff_rows:
                result.differences = pa.Table.from_pandas(pd.DataFrame(diff_rows))
        else:
            result.matched_rows = 0

        return result
