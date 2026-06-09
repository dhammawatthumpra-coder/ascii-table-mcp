#!/usr/bin/env python3
"""ASCII Table MCP Server — wcwidth-aware table rendering for Thai/Pali/CJK.

Tools:
  - make_table:            Render headers + rows as table
  - make_table_from_csv:   Parse CSV string and render
  - make_table_from_json:  Render a JSON array as table
  - make_table_preview:    Print an example table
  - analyze_table:         Analyze column positions in grid tables
  - validate_table_text:   Validate table structural integrity
  - debug_table:           Render table with position diagnostics
"""

import sys
import json
import csv
import io

from ascii_table_mcp.generate_table import (
    render_table,
    render_table_safe,
    render_table_debug,
    render_pipe_table,
    render_ascii_grid,
    analyze_grid_table,
    validate_table,
    detect_format,
    TABLE_STYLES,
    STYLE_NAMES,
)
from mcp.server.fastmcp import FastMCP

server = FastMCP("ASCII Table Generator", log_level="WARNING")


def _format_output(rows, fmt, style="mysql", auto_format=True):
    if fmt == "pipe":
        return render_pipe_table(rows)
    elif fmt == "grid":
        return render_ascii_grid(rows, style=style, auto_format=auto_format)
    elif fmt == "safe":
        return render_table_safe(rows)
    else:
        return render_table(rows)


def _finish(output, fmt):
    if fmt == "pipe":
        return output
    return f"```text\n{output}\n```"


@server.tool()
def make_table(
    headers: list[str] | None = None,
    rows: list[list[str]] | None = None,
    data: list[list[str]] | None = None,
    fmt: str = "grid",
    style: str = "mysql",
    auto_format: bool = True,
) -> str:
    """Render data as a table.

    Args:
        headers: Optional list of column header strings
        rows: List of data rows, each a list of strings
        data: Alias for rows -- pass data here if you prefer (cannot use both)
        fmt: "grid" (default) for ASCII grid, "box" for Unicode box-drawing,
             "pipe" for Markdown pipe table, "safe" for char-count padding
        style: Table style (for grid fmt). One of:
               mysql, separated, compact, gfm, reddit, rounded,
               rst, box, unicode, dots
        auto_format: Auto-detect numeric columns (right-align) and center headers

    Returns:
        Formatted table as a Markdown code block (grid/box/safe) or raw pipe table.
    """
    r = rows if rows is not None else (data if data is not None else [])
    if not r:
        return "(no data provided -- pass rows= or data=)"
    all_rows = [headers] + r if headers else r
    return _finish(_format_output(all_rows, fmt, style=style, auto_format=auto_format), fmt)

@server.tool()
def make_table_from_csv(
    csv_text: str,
    delimiter: str = ",",
    has_header: bool = True,
    fmt: str = "grid",
    style: str = "mysql",
    auto_format: bool = True,
) -> str:
    """Parse a CSV/TSV string and render as a table.

    Args:
        csv_text: Raw CSV-formatted text
        delimiter: Field delimiter (default: comma). Use '\\\\t' for TSV.
        has_header: If True (default), first row is treated as column headers
        fmt: "grid" (default), "box", "safe", or "pipe"
        style: Table style (for grid fmt)
        auto_format: Auto-detect numeric columns

    Returns:
        Formatted table.
    """
    if delimiter == "\\\\t":
        delimiter = "\t"
    reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
    parsed = list(reader)
    if not parsed:
        return "(empty CSV data)"
    all_rows = [parsed[0]] + parsed[1:] if has_header else parsed
    return _finish(_format_output(all_rows, fmt, style=style, auto_format=auto_format), fmt)


@server.tool()
def make_table_from_json(
    json_data: str,
    has_header: bool = True,
    fmt: str = "grid",
    style: str = "mysql",
    auto_format: bool = True,
) -> str:
    """Parse a JSON array and render as a table.

    Accepts either:
      - A 2D array: [["Name", "Value"], ["alpha", "1"], ...]
      - An object with "headers" and "rows" keys: {"headers":["Name"], "rows":[["alpha"]]}

    Args:
        json_data: JSON string
        has_header: If True (default), first row is treated as column headers
        fmt: "grid" (default), "box", "safe", or "pipe"
        style: Table style (for grid fmt)
        auto_format: Auto-detect numeric columns

    Returns:
        Formatted table.
    """
    try:
        parsed = json.loads(json_data)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON -- {e}"
    if isinstance(parsed, dict):
        h = parsed.get("headers", [])
        r = parsed.get("rows", [])
        all_rows = [h] + r if h else r
    elif isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], list):
        all_rows = [parsed[0]] + parsed[1:] if has_header else parsed
    else:
        return "Error: Expected a 2D array or {headers, rows} object"
    return _finish(_format_output(all_rows, fmt, style=style, auto_format=auto_format), fmt)


@server.tool()
def make_table_preview(style: str = "thai", fmt: str = "grid",
                       table_style: str = "mysql") -> str:
    """Print a preview/example table with sample data.

    Args:
        style: "thai" (default) -- example with Thai/Pali characters
               "simple" -- plain English example
        fmt: "grid" (default), "box", "pipe", or "safe"
        table_style: Table style for grid fmt (mysql, separated, etc.)

    Returns:
        Formatted example table.
    """
    if style == "thai":
        rows = [
            ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
            ["กมฺม", "kamma", "นาม", "กรรม"],
            ["อวิชฺชา", "avijjā", "กิเลส", "ความไม่รู้"],
        ]
    else:
        rows = [
            ["Name", "Role", "Status"],
            ["Alice", "Admin", "Active"],
        ]
    return _finish(_format_output(rows, fmt, style=table_style), fmt)


@server.tool()
def analyze_table(table_text: str) -> str:
    """Analyze column positions in a grid table (+---+).

    Uses display-width space (via wcwidth) for position comparison,
    so Thai/Pali combining marks (พิทุ, สระบน/ล่าง) are handled correctly.

    Scans '+' markers in border lines to define column boundaries,
    then validates '|' alignment in data rows.

    Args:
        table_text: A +---+ grid table as raw text

    Returns:
        Analysis report: column positions, alignment validation, parsed cells
    """
    result = analyze_grid_table(table_text)
    lines = []
    lines.append("--- Table Analysis ---")
    lines.append(f"Columns: {result['column_count']}")
    lines.append(f"Column boundaries (display-width): {result['columns']}")
    lines.append(f"'+' at display positions: {result['plus_display_positions']}")
    lines.append(f"Valid alignment: {'✅' if result['valid'] else '❌'}")

    if result['errors']:
        lines.append(f"\nAlignment errors ({len(result['errors'])}):")
        for e in result['errors']:
            lines.append(f"  • {e}")

    lines.append(f"\nParsed cells ({len(result['cells'])} rows):")
    for i, row in enumerate(result['cells']):
        lines.append(f"  [{i}] {json.dumps(row, ensure_ascii=False)}")

    return "\n".join(lines)


@server.tool()
def validate_table_text(table_text: str) -> str:
    """Validate structural integrity of a table (box/grid/pipe).

    Auto-detects format, then checks:
      - Border/data line alternation
      - Marker positions (+, ┬, etc.) are consistent
      - Column count is stable across rows
      - First and last lines are correct border type

    Args:
        table_text: Raw table text (box, grid, or pipe format)

    Returns:
        Validation report with any structural issues
    """
    result = validate_table(table_text)
    fmt_display = {"box": "Unicode box-drawing", "grid": "ASCII grid", "pipe": "Markdown pipe"}
    lines = []
    lines.append("--- Table Validation ---")
    lines.append(f"Format: {fmt_display.get(result['format'], result['format'])}")
    lines.append(f"Columns: {result['columns']}")
    lines.append(f"Status: {'✅ Valid' if result['valid'] else '❌ Invalid'}")

    if result['line_errors']:
        lines.append(f"\nErrors ({len(result['line_errors'])}):")
        for line_no, msg in result['line_errors']:
            lines.append(f"  Line {line_no}: {msg}")

    return "\n".join(lines)


@server.tool()
def debug_table(
    headers: list[str] | None = None,
    rows: list[list[str]] | None = None,
    data: list[list[str]] | None = None,
) -> str:
    """Render and diagnose a table — shows exact character positions.

    Produces a detailed report: plain table, annotated position analysis,
    and drift comparison between border markers and data pipes.

    Args:
        headers: Optional column headers
        rows: Data rows
        data: Alias for rows

    Returns:
        Diagnostic report with position annotations
    """
    r = rows if rows is not None else (data if data is not None else [])
    if not r:
        return "(no data provided)"
    all_rows = [headers] + r if headers else r
    return render_table_debug(all_rows)


def main():
    if "--http" in sys.argv:
        import uvicorn
        uvicorn.run(server.sse_app(), host="127.0.0.1", port=8000)
    else:
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
