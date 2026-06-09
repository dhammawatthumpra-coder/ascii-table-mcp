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

    def sep(left, mid, right, inner):
        cols = [inner * (w + 2) for w in widths]
        return left + mid.join(cols) + right

    lines = []
    lines.append(sep('+', '+', '+', '-'))
    cells = [f" {pad_cell(c, widths[i])} " for i, c in enumerate(normalised[0])]
    lines.append('|' + '|'.join(cells) + '|')
    if len(normalised) > 1:
        lines.append(sep('+', '+', '+', '-'))
        for row in normalised[1:]:
            cells = [f" {pad_cell(c, widths[i])} " for i, c in enumerate(row)]
            lines.append('|' + '|'.join(cells) + '|')
    lines.append(sep('+', '+', '+', '-'))
    return '\n'.join(lines)


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


def render_table(rows):
    """Render list-of-lists as Unicode box-drawing table."""
    if not rows:
        return "(empty table)"
    
    col_count = max(len(r) for r in rows)
    normalised = [r + [''] * (col_count - len(r)) for r in rows]
    widths = get_column_widths(normalised, col_count)

    def sep(left, mid, right, inner):
        cols = []
        for w in widths:
            cols.append(inner * (w + 2))
        return left + mid.join(cols) + right

    lines = []
    # 1. เส้นขอบบนสุด
    lines.append(sep('┌', '┬', '┐', '─'))
    
    # 2. แถวข้อมูลหัวข้อ (Header)
    cells = [f" {pad_cell(c, widths[i])} " for i, c in enumerate(normalised[0])]
    lines.append('│' + '│'.join(cells) + '│')
    
    # 3. ข้อมูลเนื้อหา (Rows)
    if len(normalised) > 1:
        lines.append(sep('├', '┼', '┤', '─'))
        for row in normalised[1:]:
            cells = [f" {pad_cell(c, widths[i])} " for i, c in enumerate(row)]
            lines.append('│' + '│'.join(cells) + '│')
            
    # 4. เส้นขอบล่างสุด
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