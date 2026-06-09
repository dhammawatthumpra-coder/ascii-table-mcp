"""Demo: create grid table → analyze it."""
import sys
sys.path.insert(0, r'F:\_Ai\ascii-table-mcp')
from generate_table import render_ascii_grid, analyze_grid_table, _display_width
import json

# 1. Render a grid table
data = [
    ["คำบาลี",    "Roman",             "หมวด",   "ความหมาย"],
    ["กมฺม",      "kamma",             "นาม",    "กรรม"],
    ["กามจฺฉนฺท",  "kāmacchanda",       "นิวรณ์",  "ความพอใจในกาม"],
    ["อวิชฺชา",    "avijjā",            "กิเลส",   "ความไม่รู้"],
    ["ปฏิจจสมุปฺปาท", "paṭiccasamuppāda", "ธรรม",   "เหตุปัจจัยต่อเนื่อง"],
    ["ธมฺม",      "dhamma",            "ทั่วไป",  "ธรรม/คำสอน"],
    ["สติ",       "sati",              "เจตสิก",  "ความระลึกได้"],
]

rendered = render_ascii_grid(data)
print("=== Rendered Table ===")
print(rendered)
print()

# 2. Show char positions vs display positions
print("=== Position Analysis ===")
for line in rendered.split("\n"):
    chars = list(enumerate(line))
    plus_pipes = [(i, ch, _display_width(line[:i])) for i, ch in enumerate(line) if ch in "+|"]
    pos_str = "  ".join(f"{ch}@{i}(dw{dw})" for i, ch, dw in plus_pipes)
    print(f"  {pos_str}  <- {line}")

# 3. Analyze
result = analyze_grid_table(rendered)
print()
print("=== Analyze Result ===")
print(f"  Valid: {result['valid']}")
print(f"  Columns: {result['column_count']}")
print(f"  Column boundaries (display-width): {result['columns']}")
print(f"  '+' at display positions: {result['plus_display_positions']}")
print()
print("  Parsed cells:")
for i, row in enumerate(result['cells']):
    print(f"    [{i}] {row}")