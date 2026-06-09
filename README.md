# ASCII Table MCP Server

```text
+---------------+------------------+--------+---------------------+
| คำบาลี        | Roman            | หมวด   | ความหมาย            |
+---------------+------------------+--------+---------------------+
| ปฏิจจสมุปฺปาท | paṭiccasamuppāda | ธรรม   | เหตุปัจจัยต่อเนื่อง |
| กามจฺฉนฺท     | kāmacchanda      | นิวรณ์ | ความพอใจในกาม       |
| อวิชฺชา       | avijjā           | กิเลส  | ความไม่รู้          |
+---------------+------------------+--------+---------------------+
```

**ตารางภาษาไทย + Roman + ตัวเลข → alignment ตรงทุกบรรทัด**

MCP server สำหรับสร้างตาราง (ASCII grid / Unicode box-drawing) ที่รองรับภาษาไทย บาลี โรมัน และ CJK อย่างถูกต้อง — ใช้ `wcwidth` ในการวัดความกว้างตัวอักษร ไม่ใช้ `len()` ที่นับผิด

---

## Features

- **3 formats**: `grid` (ASCII `+---+`), `box` (Unicode `┌─┬─┐`), `pipe` (Markdown `| | |`)
- **Thai/Pali/CJK**: zero-width combining marks (พินทุ, สระบน/ล่าง) alignment ไม่เพี้ยน
- **Safe mode**: char-count padding สำหรับ platform ที่ zero-width ≠ 0
- **5 MCP tools**: `make_table`, `make_table_from_csv`, `make_table_from_json`, `make_table_preview`, `debug_table`
- **Validation**: `validate_table_text` ตรวจสอบโครงสร้างตาราง, `analyze_table` วิเคราะห์ alignment
- **Zero external dependencies** (beyond `mcp` + `wcwidth`)

---

## Quick Start

### uvx (no install)

```bash
uvx --from git+https://github.com/dhammawatthumpra-coder/ascii-table-mcp ascii-table-mcp
```

### pip install

```bash
git clone https://github.com/dhammawatthumpra-coder/ascii-table-mcp.git
cd ascii-table-mcp
pip install -e .
python -m ascii_table_mcp
```

### Register with Claude Desktop

```json
{
  "mcpServers": {
    "ascii-table": {
      "command": "python",
      "args": ["-m", "ascii_table_mcp"]
    }
  }
}
```

### Register with Hermes

```bash
# หลังจาก pip install -e . แล้ว
hermes mcp add ascii-table --command "python -m ascii_table_mcp"
```

---

## MCP Tools

### `make_table`

สร้างตารางจาก headers + rows

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headers` | `list[str]` | — | หัวตาราง |
| `rows` / `data` | `list[list[str]]` | — | แถวข้อมูล |
| `fmt` | `str` | `"box"` | `"grid"`, `"box"`, `"pipe"`, `"safe"` |

```json
{
  "headers": ["ชื่อไฟล์", "หน้าที่", "สถานะ"],
  "rows": [
    ["generate_table.py", "core rendering engine", "✅"],
    ["server.py", "MCP wrapper", "✅"],
    ["README.md", "documentation", "✅"]
  ],
  "fmt": "grid"
}
```

ผลลัพธ์:

```text
+---------------------+-----------------------+-------+
| ชื่อไฟล์             | หน้าที่               | สถานะ  |
+---------------------+-----------------------+-------+
| generate_table.py   | core rendering engine | ✅    |
| server.py           | MCP wrapper           | ✅    |
| README.md           | documentation         | ✅    |
+---------------------+-----------------------+-------+
```

### `make_table_from_csv`

```json
{
  "csv_text": "คำบาลี,Roman,หมวด,ความหมาย\\nกมฺม,kamma,นาม,กรรม",
  "fmt": "grid"
}
```

### `make_table_from_json`

```json
{
  "json_data": "[ [\"คำ\",\"แปล\"], [\"กมฺม\",\"kamma\"], [\"อวิชฺชา\",\"avijjā\"] ]",
  "fmt": "grid"
}
```

### `debug_table`

แสดงตำแหน่ง char@pos และ drift analysis สำหรับ debugging alignment:

```text
┌───────┬───────┐
│ คำบาลี │ Roman │ ← │@char9 vs ┬@char8 ❌ drift=1
├───────┼───────┤
│ กมฺม   │ kamma │ ← ✅ align
└───────┴───────┘
```

### `analyze_table`

วิเคราะห์ column positions ของ `+--+` table และ validate `|` alignment

### `validate_table_text`

ตรวจสอบโครงสร้างตาราง: column count, border alternation, format detection

---

## Why wcwidth?

ภาษาไทยและบาลีมีอักขระ **zero-width combining marks** เช่น:

- พินทุ ( ฺ ) — `0-width` ในพจนานุกรม
- สระบน ( ิ ี ึ ื ั ) — `0-width` ติดพยัญชนะ
- สระล่าง ( ุ ู ) — `0-width`
- ไม้หันอากาศ ( ั ) — `0-width`

`len()` ใน Python นับผิด:

```text
len("กมฺม")  → 4   ❌ (นับพินทุเป็นตัวอักษร)
wcswidth("กมฺม") → 3  ✅ (พินทุ width 0)
```

ถ้าใช้ `len()` ในการจัดตาราง:

```text
+----------+-----------+   ← border ยาว 8
| คำบาลี    | Roman     |   ← "กมฺม" = 4 char → padding 4 → len=9 ❌ drift!
+----------+-----------+
```

ของเราใช้ `wcwidth.wcswidth()` แทน `len()` → alignment ตรงทุก platform

---

## Format Comparison

| Format | Example | เหมาะกับ |
|--------|---------|----------|
| `grid` | `+----+----+` | Default — terminal, code review, GitHub |
| `box` | `┌────┬────┐` | presentation, formal doc |
| `safe` | `┌────┬────┐` | Browser/Discord ที่ zero-width ≠ 0 |
| `pipe` | `\| \| \|` | Markdown, ไม่แนะนำสำหรับตารางไทย |

---

## CLI Usage

```bash
# CSV args → grid
python -m ascii_table_mcp.generate_table --grid 'ชื่อ,อายุ' 'สมชาย,30' 'สมหญิง,25'

# TSV pipe → grid
printf 'ชื่อ\tอายุ\nสมชาย\t30\n' | python -m ascii_table_mcp.generate_table --tsv --grid

# JSON
python -m ascii_table_mcp.generate_table --json '{"headers":["A","B"],"rows":[["1","2"]]}' --grid

# ASCII/Pipe Table → auto-convert
cat table.txt | python -m ascii_table_mcp.generate_table --ascii
```

```text
+--------+-------+
| ชื่อ   | อายุ  |
+--------+-------+
| สมชาย  | 30    |
| สมหญิง | 25    |
+--------+-------+
```

---

## Architecture

```text
ascii-table-mcp/
├── ascii_table_mcp/
│   ├── __init__.py      # MCP server (FastMCP)
│   └── generate_table.py # Core rendering engine
├── server.py            # Thin wrapper for `python server.py`
├── requirements.txt     # mcp + wcwidth
├── pyproject.toml        # uv / pip install
├── ascii-table-mcp.bat  # Windows wrapper
├── LICENSE              # MIT
└── README.md            # เอกสารนี้
```

Core rendering (`render_table`, `render_ascii_grid`, `render_pipe_table`, `render_table_safe`) อยู่ใน `generate_table.py` — server.py import มาใช้ ไม่มี code ซ้ำ

---

## Related

- [dmarsters/ascii-art-mcp](https://github.com/dmarsters/ascii-art-mcp) — decorative ASCII art (shaded boxes, styled tables)
- [wcwidth](https://pypi.org/project/wcwidth/) — Python port of wcwidth(3)

---

## License

MIT — แจกฟรี ใช้ได้ทั้งส่วนตัวและพาณิชย์
