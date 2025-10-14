"""
Tests for the CLI module.
"""

import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from click.testing import CliRunner

from tablediff_arrow.cli import main


@pytest.fixture
def sample_files():
    """Create sample Parquet files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        left = pa.table(
            {
                "id": [1, 2, 3, 4],
                "name": ["Alice", "Bob", "Charlie", "David"],
                "value": [10, 20, 30, 40],
            }
        )
        right = pa.table(
            {
                "id": [1, 2, 3, 5],
                "name": ["Alice", "Bob", "Charlie", "Eve"],
                "value": [10, 21, 30, 50],
            }
        )

        left_path = tmppath / "left.parquet"
        right_path = tmppath / "right.parquet"

        pq.write_table(left, left_path)
        pq.write_table(right, right_path)

        yield str(left_path), str(right_path), tmppath


def test_cli_basic(sample_files):
    """Test basic CLI usage."""
    left_path, right_path, _ = sample_files

    runner = CliRunner()
    result = runner.invoke(main, [left_path, right_path, "-k", "id"])

    assert result.exit_code == 1  # Exit code 1 for differences
    assert "Matched rows: 2" in result.output
    assert "Changed rows: 1" in result.output
    assert "Left-only rows: 1" in result.output
    assert "Right-only rows: 1" in result.output


def test_cli_html_report(sample_files):
    """Test HTML report generation via CLI."""
    left_path, right_path, tmppath = sample_files

    report_path = tmppath / "report.html"
    runner = CliRunner()
    result = runner.invoke(main, [left_path, right_path, "-k", "id", "-o", str(report_path)])

    assert result.exit_code == 1
    assert report_path.exists()
    assert "HTML report written to" in result.output


def test_cli_csv_reports(sample_files):
    """Test CSV report generation via CLI."""
    left_path, right_path, tmppath = sample_files

    csv_dir = tmppath / "csv_reports"
    runner = CliRunner()
    result = runner.invoke(main, [left_path, right_path, "-k", "id", "--csv-output", str(csv_dir)])

    assert result.exit_code == 1
    assert csv_dir.exists()
    assert (csv_dir / "diff_summary.csv").exists()


def test_cli_tolerance(sample_files):
    """Test CLI with tolerance option."""
    left_path, right_path, _ = sample_files

    runner = CliRunner()
    result = runner.invoke(main, [left_path, right_path, "-k", "id", "-t", "value:2.0"])

    assert result.exit_code == 1
    # With tolerance of 2.0, the change from 20 to 21 should be ignored
    # But we still have left-only and right-only rows


def test_cli_missing_key():
    """Test CLI with missing required key option."""
    runner = CliRunner()
    result = runner.invoke(main, ["left.parquet", "right.parquet"])

    assert result.exit_code != 0
    assert "Error" in result.output or "Missing option" in result.output


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Compare two tables" in result.output
    assert "--key" in result.output
    assert "--tolerance" in result.output
