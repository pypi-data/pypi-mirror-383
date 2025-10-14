"""
Tests for the reports module.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pytest

from tablediff_arrow.compare import TableDiff
from tablediff_arrow.reports import generate_csv_report, generate_html_report


@pytest.fixture
def sample_diff_result():
    """Create a sample DiffResult for testing."""
    left = pa.table(
        {
            "id": [1, 2, 3, 4],
            "value": [10.0, 20.0, 30.0, 40.0],
        }
    )
    right = pa.table(
        {
            "id": [1, 2, 3, 5],
            "value": [10.0, 21.0, 30.0, 50.0],
        }
    )

    differ = TableDiff(key_columns=["id"])
    return differ.compare_tables(left, right)


def test_generate_html_report(sample_diff_result):
    """Test HTML report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "report.html"
        generate_html_report(sample_diff_result, output_path)

        assert output_path.exists()
        html_content = output_path.read_text()

        # Check for key elements in HTML
        assert "Table Diff Report" in html_content
        assert "Summary" in html_content
        assert "Matched rows" in html_content
        assert str(sample_diff_result.matched_rows) in html_content


def test_generate_csv_report(sample_diff_result):
    """Test CSV report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generate_csv_report(sample_diff_result, output_dir, prefix="test")

        # Check that summary file was created
        summary_path = output_dir / "test_summary.csv"
        assert summary_path.exists()

        # Verify summary content
        summary_df = pd.read_csv(summary_path)
        assert "metric" in summary_df.columns
        assert "value" in summary_df.columns
        assert "matched_rows" in summary_df["metric"].values

        # Check for changes file if there are changes
        if sample_diff_result.differences is not None:
            changes_path = output_dir / "test_changes.csv"
            assert changes_path.exists()

        # Check for left_only file if there are left-only rows
        if sample_diff_result.left_only is not None:
            left_only_path = output_dir / "test_left_only.csv"
            assert left_only_path.exists()

        # Check for right_only file if there are right-only rows
        if sample_diff_result.right_only is not None:
            right_only_path = output_dir / "test_right_only.csv"
            assert right_only_path.exists()


def test_html_report_no_differences():
    """Test HTML report generation when there are no differences."""
    left = pa.table({"id": [1, 2], "value": [10.0, 20.0]})
    right = pa.table({"id": [1, 2], "value": [10.0, 20.0]})

    differ = TableDiff(key_columns=["id"])
    result = differ.compare_tables(left, right)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "report.html"
        generate_html_report(result, output_path)

        assert output_path.exists()
        html_content = output_path.read_text()

        # Should indicate tables match
        assert "TABLES MATCH" in html_content or "Matched rows" in html_content
