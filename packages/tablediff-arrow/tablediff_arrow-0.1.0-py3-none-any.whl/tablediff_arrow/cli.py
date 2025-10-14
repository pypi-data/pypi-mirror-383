"""
Command-line interface for tablediff-arrow.
"""

import sys

import click

from .compare import TableDiff
from .reports import generate_csv_report, generate_html_report


@click.command()
@click.argument("left", type=click.Path(exists=True))
@click.argument("right", type=click.Path(exists=True))
@click.option(
    "--key",
    "-k",
    multiple=True,
    required=True,
    help="Key column(s) for comparison. Can be specified multiple times.",
)
@click.option(
    "--tolerance",
    "-t",
    multiple=True,
    help='Absolute tolerance for numeric columns in format "column:value". '
    "Example: --tolerance amount:0.01",
)
@click.option(
    "--relative-tolerance",
    "-r",
    multiple=True,
    help='Relative tolerance for numeric columns in format "column:value". '
    "Example: --relative-tolerance price:0.001",
)
@click.option(
    "--left-format",
    type=click.Choice(["parquet", "csv", "arrow"], case_sensitive=False),
    help="Format of the left file. If not specified, inferred from extension.",
)
@click.option(
    "--right-format",
    type=click.Choice(["parquet", "csv", "arrow"], case_sensitive=False),
    help="Format of the right file. If not specified, inferred from extension.",
)
@click.option(
    "--output",
    "-o",
    help="Output file path for HTML report. If not specified, prints summary to console.",
)
@click.option(
    "--csv-output",
    type=click.Path(),
    help="Output directory for CSV reports. Generates separate files for changes, "
    "left-only, and right-only rows.",
)
@click.option("--s3", is_flag=True, help="Enable S3 filesystem support for reading files from S3.")
def main(
    left: str,
    right: str,
    key: tuple,
    tolerance: tuple,
    relative_tolerance: tuple,
    left_format: str | None,
    right_format: str | None,
    output: str | None,
    csv_output: str | None,
    s3: bool,
):
    """
    Compare two tables and generate diff reports.

    LEFT: Path to the left/source table file (local or s3://)

    RIGHT: Path to the right/target table file (local or s3://)

    Examples:

        # Compare two Parquet files using 'id' as key
        tablediff left.parquet right.parquet -k id

        # Compare with numeric tolerance
        tablediff left.csv right.csv -k id -t amount:0.01

        # Generate HTML report
        tablediff left.parquet right.parquet -k id -o report.html

        # Compare S3 files
        tablediff s3://bucket/left.parquet s3://bucket/right.parquet -k id --s3
    """
    # Parse tolerances
    abs_tolerance = {}
    for tol in tolerance:
        try:
            col, val = tol.split(":", 1)
            abs_tolerance[col] = float(val)
        except ValueError:
            click.echo(
                f"Error: Invalid tolerance format '{tol}'. Expected 'column:value'", err=True
            )
            sys.exit(1)

    rel_tolerance = {}
    for tol in relative_tolerance:
        try:
            col, val = tol.split(":", 1)
            rel_tolerance[col] = float(val)
        except ValueError:
            click.echo(
                f"Error: Invalid relative tolerance format '{tol}'. Expected 'column:value'",
                err=True,
            )
            sys.exit(1)

    # Setup filesystem for S3
    filesystem = None
    if s3 or left.startswith("s3://") or right.startswith("s3://"):
        try:
            import s3fs

            filesystem = s3fs.S3FileSystem()
        except ImportError:
            click.echo(
                "Error: s3fs is required for S3 access. "
                "Install with: pip install tablediff-arrow[s3]",
                err=True,
            )
            sys.exit(1)

    # Create TableDiff instance
    differ = TableDiff(
        key_columns=list(key),
        tolerance=abs_tolerance,
        relative_tolerance=rel_tolerance,
    )

    # Perform comparison
    try:
        click.echo("Loading tables...")
        result = differ.compare_files(
            left,
            right,
            left_format=left_format,
            right_format=right_format,
            filesystem=filesystem,
        )

        # Print summary
        click.echo("\n" + result.summary())

        # Generate HTML report if requested
        if output:
            click.echo(f"\nGenerating HTML report: {output}")
            generate_html_report(result, output)
            click.echo(f"HTML report written to {output}")

        # Generate CSV reports if requested
        if csv_output:
            click.echo(f"\nGenerating CSV reports in: {csv_output}")
            generate_csv_report(result, csv_output)
            click.echo(f"CSV reports written to {csv_output}")

        # Exit with non-zero code if differences found
        if result.has_differences:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
