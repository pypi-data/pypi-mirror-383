"""
Tests for the comparison module.
"""

import pyarrow as pa
import pytest

from tablediff_arrow.compare import DiffResult, TableDiff


@pytest.fixture
def identical_tables():
    """Create two identical tables."""
    table = pa.table(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.0, 20.0, 30.0],
        }
    )
    return table, table


@pytest.fixture
def tables_with_changes():
    """Create tables with some changed values."""
    left = pa.table(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.0, 20.0, 30.0],
        }
    )
    right = pa.table(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.0, 21.0, 30.0],  # Changed value for id=2
        }
    )
    return left, right


@pytest.fixture
def tables_with_added_removed():
    """Create tables with added and removed rows."""
    left = pa.table(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.0, 20.0, 30.0],
        }
    )
    right = pa.table(
        {
            "id": [1, 3, 4],  # Removed id=2, added id=4
            "name": ["Alice", "Charlie", "David"],
            "value": [10.0, 30.0, 40.0],
        }
    )
    return left, right


def test_identical_tables(identical_tables):
    """Test comparison of identical tables."""
    left, right = identical_tables
    differ = TableDiff(key_columns=["id"])
    result = differ.compare_tables(left, right)

    assert result.matched_rows == 3
    assert result.changed_rows == 0
    assert result.left_only_rows == 0
    assert result.right_only_rows == 0
    assert not result.has_differences


def test_tables_with_changes(tables_with_changes):
    """Test comparison of tables with changed values."""
    left, right = tables_with_changes
    differ = TableDiff(key_columns=["id"])
    result = differ.compare_tables(left, right)

    assert result.matched_rows == 2
    assert result.changed_rows == 1
    assert result.left_only_rows == 0
    assert result.right_only_rows == 0
    assert result.total_changes == 1
    assert "value" in result.column_changes
    assert result.column_changes["value"] == 1
    assert result.has_differences


def test_tables_with_added_removed(tables_with_added_removed):
    """Test comparison of tables with added and removed rows."""
    left, right = tables_with_added_removed
    differ = TableDiff(key_columns=["id"])
    result = differ.compare_tables(left, right)

    assert result.matched_rows == 2
    assert result.changed_rows == 0
    assert result.left_only_rows == 1
    assert result.right_only_rows == 1
    assert result.has_differences
    assert result.left_only is not None
    assert result.right_only is not None


def test_absolute_tolerance():
    """Test absolute tolerance for numeric comparisons."""
    left = pa.table(
        {
            "id": [1, 2, 3],
            "value": [10.0, 20.0, 30.0],
        }
    )
    right = pa.table(
        {
            "id": [1, 2, 3],
            "value": [10.01, 20.02, 30.00],  # Small differences
        }
    )

    # Without tolerance, should find differences
    differ = TableDiff(key_columns=["id"])
    result = differ.compare_tables(left, right)
    assert result.changed_rows == 2

    # With tolerance, should not find differences
    differ = TableDiff(key_columns=["id"], tolerance={"value": 0.05})
    result = differ.compare_tables(left, right)
    assert result.changed_rows == 0


def test_relative_tolerance():
    """Test relative tolerance for numeric comparisons."""
    left = pa.table(
        {
            "id": [1, 2],
            "value": [100.0, 1000.0],
        }
    )
    right = pa.table(
        {
            "id": [1, 2],
            "value": [100.5, 1005.0],  # 0.5% and 0.5% difference
        }
    )

    # Without tolerance, should find differences
    differ = TableDiff(key_columns=["id"])
    result = differ.compare_tables(left, right)
    assert result.changed_rows == 2

    # With 1% relative tolerance, should not find differences
    differ = TableDiff(key_columns=["id"], relative_tolerance={"value": 0.01})
    result = differ.compare_tables(left, right)
    assert result.changed_rows == 0


def test_multiple_key_columns():
    """Test comparison with multiple key columns."""
    left = pa.table(
        {
            "year": [2020, 2020, 2021],
            "month": [1, 2, 1],
            "value": [10.0, 20.0, 30.0],
        }
    )
    right = pa.table(
        {
            "year": [2020, 2020, 2021],
            "month": [1, 2, 1],
            "value": [10.0, 21.0, 30.0],  # Changed value for 2020-02
        }
    )

    differ = TableDiff(key_columns=["year", "month"])
    result = differ.compare_tables(left, right)

    assert result.matched_rows == 2
    assert result.changed_rows == 1
    assert result.total_changes == 1


def test_missing_key_column():
    """Test that missing key column raises an error."""
    left = pa.table({"id": [1, 2], "value": [10.0, 20.0]})
    right = pa.table({"id": [1, 2], "value": [10.0, 20.0]})

    differ = TableDiff(key_columns=["missing_col"])

    with pytest.raises(ValueError, match="Key column 'missing_col' not found"):
        differ.compare_tables(left, right)


def test_diff_result_summary():
    """Test DiffResult summary generation."""
    result = DiffResult(
        matched_rows=10,
        changed_rows=2,
        left_only_rows=1,
        right_only_rows=1,
        total_changes=5,
        column_changes={"col1": 3, "col2": 2},
    )

    summary = result.summary()
    assert "Matched rows: 10" in summary
    assert "Changed rows: 2" in summary
    assert "Left-only rows: 1" in summary
    assert "Right-only rows: 1" in summary
    assert "Total changes: 5" in summary
    assert "col1: 3" in summary
    assert "col2: 2" in summary
