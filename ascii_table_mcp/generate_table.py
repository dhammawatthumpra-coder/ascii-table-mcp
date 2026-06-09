#!/usr/bin/env python3
"""Generate tables with correct East Asian width.

Output formats:
  box-drawing (default)  ┌─┬─┐ style (Unicode)
  pipe                   | | | style (Markdown pipe table)

Usage:
  python3 generate_table.py 'header1,header2' 'r1c1,r1c2' 'r2c1,r2c2' ...

Or pipe raw TSV:
  printf 'Name\tCPU\tMEM\nnode\t2\t4GB\n' | python3 generate_table.py --tsv

Or JSON:
  python3 generate_table.py --json '{"headers":["A"],"rows":[["1"]]}'

Or pipe table output:
  python3 generate_table.py --pipe 'header1,header2' 'val1,val2'

Or Auto-convert ASCII/Pipe Table to box-drawing:
  cat table.txt | python3 generate_table.py --ascii

Width handling:
  - Uses wcwidth/wcswidth for East Asian characters (Thai, CJK)
  - Zero-width combining marks (พินทุ, ไม้หันอากาศ, สระบน/ล่าง) counted correctly
  - Falls back to len() on ImportError (no wcwidth installed)
"""

import sys
import csv
import json

# ─── Display width: wcwidth directly (Thai/Pali combining marks handled correctly) ───
try:
    from wcwidth import wcswidth
    def _display_width(s: str) -> int:
        w = wcswidth(str(s))
        return w if w >= 0 else len(str(s))
except ImportError:
    def _display_width(s: str) -> int:
        return len(str(s))


def get_column_widths(rows, col_count):
    """Compute display width of each column using _display_width()."""
    widths = [0] * col_count
    for row in rows:
        for i, cell in enumerate(row):
            w = _display_width(cell)
            if w > widths[i]:
                widths[i] = w
    return widths


def pad_cell(s, width):
    """Pad string to display width using _display_width()."""
    s = str(s)
    diff = width - _display_width(s)
    if diff > 0:
        s += ' ' * diff
    return s


def parse_ascii_table(text):
    """Parse traditional ASCII/Pipe table into rows list."""
    lines = text.strip().split('\n')
    rows = []
    for line in lines:
        # ข้ามเส้นคั่นตารางพวก +----+ หรือ ----
        if line.strip().startswith('+') or line.strip().startswith('-'):
            continue
        if '|' in line:
            # แยกเซลล์ด้วย | และลบช่องว่างส่วนเกินออก
            cells = [c.strip() for c in line.split('|')]
            # ตัดเซลล์ว่างหัวท้ายที่เกิดจากเครื่องหมาย | ปิดหน้าหลังตาราง
            if cells[0] == '': cells.pop(0)
            if cells and cells[-1] == '': cells.pop()
            if cells:
                rows.append(cells)
    return rows


def detect_format(text):
    """Auto-detect table format from text."""
    lines = text.strip().split('\n')
    if not lines:
        return 'unknown'
    first = lines[0].strip()
    if first.startswith('┌') and first.endswith('┐'):
        return 'box'
    if first.startswith('+') and first.endswith('+'):
        return 'grid'
    if '|' in first and '|' in lines[-1]:
        return 'pipe'
    return 'unknown'


def validate_table(text):
    """Validate structural integrity of a grid/box/pipe table.

    Checks:
      - Border/data line alternation
      - Marker positions (+, |) are consistent
      - Column count stable
      - First/last lines are correct border type

    Returns dict: valid, format, line_errors (list of (line_no, msg))
    """
    lines = text.split('\n')
    fmt = detect_format(text)
    errors = []
    border_markers = []

    if fmt == 'box':
        # Border chars in box-drawing: ┌┬┐ ├┼┤ └┴┘ are all structural markers
        all_box = '┬┼┴┌┐├┤└┘'
        sep_chars = '┬┼┴'
    elif fmt == 'grid':
        all_box = '+'
        sep_chars = '+'
    elif fmt == 'pipe':
        all_box = '-'
        sep_chars = '-'
    else:
        return {"valid": False, "format": fmt, "line_errors": [(0, "unknown table format")]}

    border_markers = []

    for i, line in enumerate(lines):
        if not line.strip():
            errors.append((i + 1, 'empty line'))
            continue

        first = line.strip()[0]
        if first in ('┌', '├', '└', '+', '-'):
            # Border line
            markers = [j for j, ch in enumerate(line) if ch in sep_chars]
            if not border_markers:
                border_markers = markers
            elif markers != border_markers:
                marker_diff = set(markers) ^ set(border_markers)
                errors.append((i + 1, f'border markers differ: +/-{sorted(marker_diff)}'))
        elif first == '│' or first == '|':
            # Data line
            pipe_count = len([j for j, ch in enumerate(line) if ch in '│|'])
            expected_pipes = len(border_markers)  # grid/pipe
            if fmt == 'box':
                expected_pipes = len(border_markers) + 2  # ┌┬┐ → │ │ │ │
            if expected_pipes > 0 and pipe_count != expected_pipes:
                errors.append((i + 1, f'data has {pipe_count} pipes, expected {expected_pipes}'))
        else:
            errors.append((i + 1, f'unexpected start char: {repr(first)}'))

    return {
        "valid": len(errors) == 0,
        "format": fmt,
        "columns": len(border_markers) + 1 if fmt == 'box' else max(0, len(border_markers) - 1),
        "line_errors": errors,
    }


def analyze_grid_table(text):
    """Analyze column positions in a +---+ grid table.

    Uses _display_width() for position comparison, so handles Thai/Pali
    combining marks (พินทุ, สระบน/ล่าง) correctly.

    Returns:
        dict with columns (list of (d_start, d_end)), errors, cells
    """
    lines = text.strip().split('\n')
    if not lines:
        return {"columns": [], "errors": ["empty input"], "cells": []}

    # Find a border line (starts with +)
    border = None
    for line in lines:
        s = line.strip()
        if s.startswith('+'):
            border = s
            break

    if border is None:
        return {"columns": [], "errors": ["no border line (+---+) found"], "cells": []}

    # Find '+' positions — using display width (all ASCII so char = display)
    plus_chars = [i for i, ch in enumerate(border) if ch == '+']
    if len(plus_chars) < 2:
        return {"columns": [], "errors": ["need at least 2 '+' markers"], "cells": []}

    # Translate char positions to display-width positions (for ASCII, identical)
    def char_to_display(s, char_idx):
        return _display_width(s[:char_idx])

    plus_display = [char_to_display(border, p) for p in plus_chars]

    # Columns in display-width space
    columns = []
    for i in range(len(plus_display) - 1):
        columns.append((plus_display[i], plus_display[i + 1]))

    errors = []
    cells = []

    for i, line in enumerate(lines):
        s = line.rstrip('\n').rstrip('\r')
        if s.strip().startswith('+'):
            continue
        if '|' not in s:
            continue

        # Find '|' positions in display-width space
        pipe_display = [
            char_to_display(s, j)
            for j, ch in enumerate(s) if ch == '|'
        ]

        expected = plus_display[:]

        if pipe_display != expected:
            errors.append(
                f"line {i+1}: | at display positions {pipe_display} "
                f"!= expected {expected} (char pos mismatch due to Thai/Pali width)"
            )

        # Extract cells using display-width-based slicing
        row_cells = []
        for col_d_start, col_d_end in columns:
            # Find char position where display width matches col_d_start + 1 (past '|')
            cell_start_d = col_d_start + 1
            cell_end_d = col_d_end
            # Scan to find char range matching this display-width range
            acc = 0
            start_char = None
            end_char = len(s)
            for ci, ch in enumerate(s):
                w = _display_width(ch)
                if acc <= cell_start_d < acc + w and start_char is None:
                    start_char = ci
                if acc < cell_end_d <= acc + w:
                    end_char = ci
                    break
                acc += w
            if start_char is None:
                start_char = 0
            cell_text = s[start_char:end_char].strip()
            row_cells.append(cell_text)
        cells.append(row_cells)

    return {
        "columns": columns,
        "plus_display_positions": plus_display,
        "plus_char_positions": plus_chars,
        "errors": errors,
        "cells": cells,
        "column_count": len(columns),
        "valid": len(errors) == 0,
    }


def render_ascii_grid(rows):
    """Render list-of-lists as ASCII grid table (+---+ style).

    This format is simpler than Unicode box-drawing (no multi-byte chars),
    easier to parse/reverse, and works everywhere.
    """
    if not rows:
        return "(empty table)"

    col_count = max(len(r) for r in rows)
    normalised = [r + [''] * (col_count - len(r)) for r in rows]
    widths = get_column_widths(normalised, col_count)

    # padded_lens = char-count after padding (for correct border length)
    padded_lens = [0] * col_count
    for row in normalised:
        for i, cell in enumerate(row):
            padded = pad_cell(cell, widths[i])
            total = len(padded) + 2
            if total > padded_lens[i]:
                padded_lens[i] = total

    def sep(left, mid, right, inner):
        cols = [inner * padded_lens[i] for i in range(col_count)]
        return left + mid.join(cols) + right

    lines = []
    lines.append(sep('+', '+', '+', '-'))
    cells = [_fmt_cell(c, i, widths, padded_lens) for i, c in enumerate(normalised[0])]
    lines.append('|' + '|'.join(cells) + '|')
    if len(normalised) > 1:
        lines.append(sep('+', '+', '+', '-'))
        for row in normalised[1:]:
            cells = [_fmt_cell(c, i, widths, padded_lens) for i, c in enumerate(row)]
            lines.append('|' + '|'.join(cells) + '|')
    lines.append(sep('+', '+', '+', '-'))
    return '\n'.join(lines)


def _fmt_cell(cell, col_idx, widths, padded_lens):
    """Format a cell with wcwidth-aware padding and extra alignment fill."""
    padded = pad_cell(cell, widths[col_idx])
    extra = padded_lens[col_idx] - len(padded) - 2
    if extra > 0:
        padded += ' ' * extra
    return f" {padded} "


def render_pipe_table(rows, top_frame=True):
    """Render list-of-lists as Markdown pipe table."""
    if not rows:
        return "(empty table)"

    col_count = max(len(r) for r in rows)
    normalised = [r + [''] * (col_count - len(r)) for r in rows]
    widths = get_column_widths(normalised, col_count)

    lines = []
    sep = '|' + '|'.join(['-' * (w + 2) for w in widths]) + '|'

    # Top frame (optional)
    if top_frame:
        lines.append(sep)

    # Header
    cells = [f" {pad_cell(c, widths[i])} " for i, c in enumerate(normalised[0])]
    lines.append('|' + '|'.join(cells) + '|')
    # Separator
    lines.append(sep)
    # Rows
    for row in normalised[1:]:
        cells = [f" {pad_cell(c, widths[i])} " for i, c in enumerate(row)]
        lines.append('|' + '|'.join(cells) + '|')
    return '\n'.join(lines)


def render_table_debug(rows):
    """Render box-drawing table with character-position annotations.

    Shows every border marker (+) and data pipe (|) with its character index
    and display-width position. Use this to diagnose alignment drift caused
    by platform rendering of zero-width combining marks.
    """
    table = render_table(rows)
    lines_out = []
    lines_out.append("═" * 60)
    lines_out.append("TABLE (plain):")
    lines_out.append("═" * 60)
    lines_out.append(table)
    lines_out.append("")
    lines_out.append("═" * 60)
    lines_out.append("POSITION ANALYSIS (char@pos | dw=display-width):")
    lines_out.append("═" * 60)
    for line in table.split("\n"):
        annotations = []
        for i, ch in enumerate(line):
            if ch in "┬┼┴┌┐├┤└┘││+|-":
                dw = _display_width(line[:i])
                annotations.append(f"  {ch}@char{i}(dw{dw})")
        if annotations:
            lines_out.append("".join(annotations) + f"  ← {line}")
        else:
            lines_out.append(f"  (no markers)  ← {line}")
    lines_out.append("")
    lines_out.append("═" * 60)
    lines_out.append("INTERPRETATION:")
    lines_out.append("═" * 60)
    
    # Build marker lists from the rendered table
    border_markers = []
    data_markers = []
    for line in table.split("\n"):
        bm = [(i, ch) for i, ch in enumerate(line) if ch in "┬┼┴"]
        if bm:
            border_markers.append(bm)
        dp = [(i, ch) for i, ch in enumerate(line) if ch in "│"]
        if dp:
            data_markers.append(dp)
    
    # Compare border internal markers vs data pipes (skip edge pipes)
    if border_markers and data_markers and len(border_markers[0]) > 0:
        ref = border_markers[0]  # first border's internal markers
        lines_out.append(f"Reference border internal markers: {ref}")
        for ridx, row in enumerate(data_markers):
            # Skip first and last pipe (edges), compare internal ones
            internal = row[1:-1]
            diffs = []
            for i, (pos, ch) in enumerate(internal):
                if i < len(ref):
                    expected_pos = ref[i][0]
                    if pos != expected_pos:
                        diffs.append(f"  col{i}: border @{expected_pos} vs pipe @{pos} (drift {pos - expected_pos})")
                    else:
                        diffs.append(f"  col{i}: aligned @{pos} ✓")
            if diffs:
                lines_out.append(f"  Data row {ridx + 1}:")
                for d in diffs:
                    lines_out.append(f"    {d}")
    
    max_drift = 0
    if border_markers and data_markers:
        ref = border_markers[0]
        for row in data_markers:
            internal = row[1:-1]  # skip edge pipes
            for i, (pos, ch) in enumerate(internal):
                if i < len(ref):
                    drift = abs(pos - ref[i][0])
                    if drift > max_drift:
                        max_drift = drift
    
    if max_drift == 0:
        lines_out.append("")
        lines_out.append("✅ Zero structural drift — all markers align in char space.")
        lines_out.append("   If visual alignment looks off, the issue is platform rendering")
        lines_out.append("   (Discord font, terminal emulator, browser code-block renderer).")
        lines_out.append("")
        lines_out.append("   Try render_table with safe=True for char-count padding.")
    else:
        lines_out.append("")
        lines_out.append(f"❌ Drift detected: max {max_drift} chars between border and data.")
    
    return "\n".join(lines_out)


def render_table_safe(rows):
    """Render box-drawing table using character-count padding.

    Unlike render_table() which uses display-width (wcwidth) for padding,
    this version pads to len() — guaranteeing structural marker alignment
    even on platforms that render combining marks with non-zero width.
    
    Safe mode trades slightly wider columns for guaranteed alignment.
    """
    if not rows:
        return "(empty table)"

    col_count = max(len(r) for r in rows)
    normalised = [r + [''] * (col_count - len(r)) for r in rows]

    # Compute max character length for each column (safe padding)
    col_max = [0] * col_count
    for row in normalised:
        for i, cell in enumerate(row):
            if len(cell) > col_max[i]:
                col_max[i] = len(cell)

    def sep(left, mid, right, inner):
        cols = [inner * (col_max[i] + 2) for i in range(col_count)]
        return left + mid.join(cols) + right

    def fmt_cell(cell, i):
        padded = cell + ' ' * (col_max[i] - len(cell))
        return f" {padded} "

    lines = []
    lines.append(sep('┌', '┬', '┐', '─'))
    cells = [fmt_cell(c, i) for i, c in enumerate(normalised[0])]
    lines.append('│' + '│'.join(cells) + '│')
    if len(normalised) > 1:
        lines.append(sep('├', '┼', '┤', '─'))
        for row in normalised[1:]:
            cells = [fmt_cell(c, i) for i, c in enumerate(row)]
            lines.append('│' + '│'.join(cells) + '│')
    lines.append(sep('└', '┴', '┘', '─'))
    return '\n'.join(lines)


def render_table(rows):
    """Render box-drawing table using wcwidth display-width padding.
    Border uses exact padded character length to keep structural
    markers (┬┼┴) aligned with data pipes (│).
    
    For guaranteed alignment on imperfect Unicode renderers, use
    render_table_safe() instead (char-count padding).
    """
    if not rows:
        return "(empty table)"

    col_count = max(len(r) for r in rows)
    normalised = [r + [''] * (col_count - len(r)) for r in rows]

    disp_widths = [0] * col_count
    for row in normalised:
        for i, cell in enumerate(row):
            dw = _display_width(cell)
            if dw > disp_widths[i]:
                disp_widths[i] = dw

    padded_lens = [0] * col_count
    for row in normalised:
        for i, cell in enumerate(row):
            padded = pad_cell(cell, disp_widths[i])
            total = len(padded) + 2
            if total > padded_lens[i]:
                padded_lens[i] = total

    def sep(left, mid, right, inner):
        cols = [inner * padded_lens[i] for i in range(col_count)]
        return left + mid.join(cols) + right

    lines = []
    lines.append(sep('┌', '┬', '┐', '─'))

    def fmt_cell(cell, i):
        padded = pad_cell(cell, disp_widths[i])
        extra = padded_lens[i] - len(padded) - 2
        if extra > 0:
            padded += ' ' * extra
        return f" {padded} "

    cells = [fmt_cell(c, i) for i, c in enumerate(normalised[0])]
    lines.append('│' + '│'.join(cells) + '│')
    if len(normalised) > 1:
        lines.append(sep('├', '┼', '┤', '─'))
        for row in normalised[1:]:
            cells = [fmt_cell(c, i) for i, c in enumerate(row)]
            lines.append('│' + '│'.join(cells) + '│')
    lines.append(sep('└', '┴', '┘', '─'))
    return '\n'.join(lines)


def main():
    """Entry point: parse args/TSV/JSON/ASCII and print table."""
    rows = []

    flags = {'--tsv', '--preview', '--json', '--ascii', '--pipe', '--grid'}
    args = [a for a in sys.argv[1:] if a not in flags]

    if '--tsv' in sys.argv:
        reader = csv.reader(sys.stdin, delimiter='\t')
        rows = list(reader)
        
    elif '--ascii' in sys.argv:
        # อ่านค่าตารางแบบเก่าจาก stdin มาแปลงอัตโนมัติ
        raw_text = sys.stdin.read()
        rows = parse_ascii_table(raw_text)
        
    elif '--preview' in sys.argv:
        rows = [
            ['id', 'namespace', 'command', 'status'],
            ['1', 'N/A', 'echo hi', 'Stopped'],
            ['2', 'N/A', 'node server.js', 'Running']
        ]
        
    elif '--json' in sys.argv:
        try:
            idx = sys.argv.index('--json')
            if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith('-'):
                data = json.loads(sys.argv[idx + 1])
            else:
                data = json.load(sys.stdin)
                
            headers = data.get('headers', [])
            rows_data = data.get('rows', [])
            rows = [headers] + rows_data if headers else rows_data
        except (json.JSONDecodeError, IndexError, ValueError):
            print("Error: Invalid JSON data specified.", file=sys.stderr)
            sys.exit(1)
            
    elif args:
        # ตรวจสอบเบื้องต้นว่าอาร์กิวเมนต์ที่ส่งมาเป็นตารางแบบเก่าหรือไม่
        full_args = " ".join(args)
        if '+' in full_args or '|' in full_args:
            rows = parse_ascii_table(full_args)
        else:
            rows = [arg.split(',') for arg in args]

    if not rows:
        print("Usage: python3 generate_table.py [OPTIONS]")
        print()
        print("  CSV args:   python3 generate_table.py 'h1,h2' 'r1c1,r1c2' [...]")
        print("  --tsv:      pipe TSV via stdin")
        print("  --json:     pass JSON data via arg or stdin")
        print("  --ascii:    pipe traditional ASCII table (+---+|...) via stdin")
        print("  --pipe:     output Markdown pipe table")
        print("  --grid:     output ASCII grid (+---+ style)")
        print("  --preview:  print example table")
        sys.exit(1)

    if '--pipe' in sys.argv:
        output = render_pipe_table(rows)
        print(output)
    elif '--grid' in sys.argv:
        output = render_ascii_grid(rows)
        print('```text')
        print(output)
        print('```')
    else:
        output = render_table(rows)
        print('```text')
        print(output)
        print('```')


if __name__ == '__main__':
    main()