"""
Report generation for table diffs (HTML and CSV formats).
"""

from pathlib import Path

import pandas as pd
from jinja2 import Template

from .compare import DiffResult

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Table Diff Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #666;
            margin-top: 30px;
        }
        .summary {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .summary-item {
            margin: 8px 0;
            font-size: 14px;
        }
        .summary-item .label {
            font-weight: bold;
            display: inline-block;
            width: 180px;
        }
        .summary-item .value {
            color: #333;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            margin-left: 10px;
        }
        .status-match {
            background-color: #4CAF50;
            color: white;
        }
        .status-diff {
            background-color: #f44336;
            color: white;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .removed {
            background-color: #ffebee;
        }
        .added {
            background-color: #e8f5e9;
        }
        .changed {
            background-color: #fff3e0;
        }
        .column-changes {
            list-style: none;
            padding-left: 0;
        }
        .column-changes li {
            padding: 4px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Table Diff Report</h1>

        <div class="summary">
            <h2>Summary
                {% if has_differences %}
                <span class="status status-diff">DIFFERENCES FOUND</span>
                {% else %}
                <span class="status status-match">TABLES MATCH</span>
                {% endif %}
            </h2>
            <div class="summary-item">
                <span class="label">Matched rows:</span>
                <span class="value">{{ matched_rows }}</span>
            </div>
            <div class="summary-item">
                <span class="label">Changed rows:</span>
                <span class="value">{{ changed_rows }}</span>
            </div>
            <div class="summary-item">
                <span class="label">Left-only rows:</span>
                <span class="value">{{ left_only_rows }}</span>
            </div>
            <div class="summary-item">
                <span class="label">Right-only rows:</span>
                <span class="value">{{ right_only_rows }}</span>
            </div>
            <div class="summary-item">
                <span class="label">Total changes:</span>
                <span class="value">{{ total_changes }}</span>
            </div>

            {% if column_changes %}
            <div class="summary-item">
                <span class="label">Changes by column:</span>
                <ul class="column-changes">
                    {% for col, count in column_changes.items() %}
                    <li>{{ col }}: {{ count }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>

        {% if differences_html %}
        <h2>Changed Values</h2>
        {{ differences_html | safe }}
        {% endif %}

        {% if left_only_html %}
        <h2>Rows Only in Left Table</h2>
        {{ left_only_html | safe }}
        {% endif %}

        {% if right_only_html %}
        <h2>Rows Only in Right Table</h2>
        {{ right_only_html | safe }}
        {% endif %}
    </div>
</body>
</html>
"""


def generate_html_report(
    result: DiffResult,
    output_path: str | Path,
) -> None:
    """
    Generate an HTML report from a DiffResult.

    Args:
        result: The DiffResult to report on
        output_path: Path to write the HTML report
    """
    template = Template(HTML_TEMPLATE)

    # Convert tables to HTML
    differences_html = None
    if result.differences is not None:
        df = result.differences.to_pandas()
        differences_html = df.to_html(index=False, classes="changed")

    left_only_html = None
    if result.left_only is not None:
        df = result.left_only.to_pandas()
        left_only_html = df.to_html(index=False, classes="removed")

    right_only_html = None
    if result.right_only is not None:
        df = result.right_only.to_pandas()
        right_only_html = df.to_html(index=False, classes="added")

    html = template.render(
        has_differences=result.has_differences,
        matched_rows=result.matched_rows,
        changed_rows=result.changed_rows,
        left_only_rows=result.left_only_rows,
        right_only_rows=result.right_only_rows,
        total_changes=result.total_changes,
        column_changes=result.column_changes,
        differences_html=differences_html,
        left_only_html=left_only_html,
        right_only_html=right_only_html,
    )

    Path(output_path).write_text(html, encoding="utf-8")


def generate_csv_report(
    result: DiffResult,
    output_dir: str | Path,
    prefix: str = "diff",
) -> None:
    """
    Generate CSV reports from a DiffResult.

    Creates separate CSV files for differences, left-only, and right-only rows.

    Args:
        result: The DiffResult to report on
        output_dir: Directory to write CSV files
        prefix: Prefix for the CSV filenames
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if result.differences is not None:
        df = result.differences.to_pandas()
        df.to_csv(output_path / f"{prefix}_changes.csv", index=False)

    if result.left_only is not None:
        df = result.left_only.to_pandas()
        df.to_csv(output_path / f"{prefix}_left_only.csv", index=False)

    if result.right_only is not None:
        df = result.right_only.to_pandas()
        df.to_csv(output_path / f"{prefix}_right_only.csv", index=False)

    # Generate summary CSV
    summary_data: dict[str, list[str | int]] = {
        "metric": [
            "matched_rows",
            "changed_rows",
            "left_only_rows",
            "right_only_rows",
            "total_changes",
        ],
        "value": [
            result.matched_rows,
            result.changed_rows,
            result.left_only_rows,
            result.right_only_rows,
            result.total_changes,
        ],
    }

    # Add column changes
    for col, count in result.column_changes.items():
        summary_data["metric"].append(f"column_{col}_changes")
        summary_data["value"].append(count)

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_path / f"{prefix}_summary.csv", index=False)
