# ASCII Table MCP Server

```text
+------------+------------------+------+---------------+
| คำบาลี      | Roman            | หมวด | ความหมาย      |
+------------+------------------+------+---------------+
| ปฏิจจสมุปฺปาท | paṭiccasamuppāda | ธรรม | เหตุปัจจัยต่อเนื่อง |
| กามจฺฉนฺท    | kāmacchanda      | นิวรณ์ | ความพอใจในกาม |
| อวิชฺชา      | avijjā           | กิเลส | ความไม่รู้       |
+------------+------------------+------+---------------+
```

**ตารางภาษาไทย + Roman + ตัวเลข → alignment ตรงทุกบรรทัด**

MCP server สำหรับสร้างตาราง (ASCII grid / Unicode box-drawing) ที่รองรับภาษาไทย บาลี โรมัน และ CJK อย่างถูกต้อง — ใช้ `wcwidth` ในการวัดความกว้างตัวอักษร ไม่ใช้ `len()` ที่นับผิด

> 🌐 **ลองใช้บนเว็บ!** → [**ASCII Table → Image Generator**](https://dhammawatthumpra-coder.github.io/ascii-table-mcp/)<br>
> วาง CSV, เลือก style, export ได้ทั้ง PNG / SVG / Grid / Box / Pipe. รองรับไทย + emoji. ไม่ต้องติดตั้ง.

![ตัวอย่าง Web Tool](examples/web_preview.png)

---

## Features

- **5 table formats**: `grid` (ASCII `+---+`), `box` (Unicode `┌─┬─┐`), `pipe` (Markdown `| | |`), `safe` (char-count padding), `html` (HTML file with Noto Sans Thai)
- **10 grid sub-styles**: `mysql`, `separated`, `compact`, `gfm`, `reddit`, `rounded`, `rst`, `box`, `unicode`, `dots`
- **Auto-format**: รองรับตัวเลข (right-align) และหัวตาราง (center) — ได้แรงบันดาลใจจาก [ozh/ascii-tables](https://github.com/ozh/ascii-tables)
- **Thai/Pali/CJK**: zero-width combining marks (พินทุ, สระบน/ล่าง) alignment ไม่เพี้ยน
- **Safe width mode**: extra padding ชดเชย platform ที่ zero-width ≠ 0 (Discord, browser code blocks)
- **7 MCP tools**: `make_table`, `make_table_from_csv`, `make_table_from_json`, `make_table_preview`, `debug_table`, `analyze_table`, `validate_table_text`
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

สร้างตารางจาก headers + rows รองรับ style, auto-format, safe width

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headers` | `list[str]` | — | หัวตาราง |
| `rows` / `data` | `list[list[str]]` | — | แถวข้อมูล |
|| `fmt` | `str` | `"grid"` | `"grid"`, `"box"`, `"pipe"`, `"safe"`, `"html"` |
| `style` | `str` | `"mysql"` | ดูตาราง Styles ด้านล่าง |
| `auto_format` | `bool` | `true` | right-align ตัวเลข, center หัวตาราง |
| `safe_width` | `bool` | `false` | extra padding สำหรับ Discord/browser |

**ตัวอย่าง:** `style="separated"` พร้อม auto-format

```json
{
  "headers": ["สินค้า", "ราคา", "จำนวน"],
  "rows": [
    ["ก๋วยเตี๋ยว", "45", "3"],
    ["ข้าวผัด", "55", "2"],
    ["รวม", "100", "5"]
  ],
  "fmt": "grid",
  "style": "separated"
}
```

ผลลัพธ์:

```text
+============+======+=======+
|   สินค้า    | ราคา | จำนวน |
+============+======+=======+
+------------+------+-------+
| ก๋วยเตี๋ยว |   45 |     3 |
+------------+------+-------+
| ข้าวผัด    |   55 |     2 |
+------------+------+-------+
| รวม        |  100 |     5 |
+------------+------+-------+
```

สังเกต: `auto_format=true` ทำให้คอลัมน์ "ราคา" กับ "จำนวน" ถูกจัดชิดขวา (ตัวเลข) หัวตารางถูกจัดกลาง

**Safe width สำหรับ Discord:**

```json
{
  "rows": [["ชื่อ", "ราคา"], ["ก๋วยเตี๋ยว", "45"]],
  "fmt": "grid",
  "safe_width": true
}
```

ผลลัพธ์มี padding เพิ่มตามจำนวน zero-width marks เพื่อชดเชย Discord/browser ที่ render marks ด้วย width > 0

**Style `compact` (ไม่มีกรอบ):**

```json
{ "headers": ["A", "B"], "rows": [["x", "1"]], "fmt": "grid", "style": "compact" }
```

```text
   A    B  
 ----- --- 
  x     1  
```

**Style `rounded`:**

```json
{ "headers": ["A"], "rows": [["x"]], "fmt": "grid", "style": "rounded" }
```

```text
.---.
| A |
:---:
| x |
'---'
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

## Thai Character Width Compensation

Discord, browser code blocks, และ terminal บางประเภท **ไม่รองรับ zero-width combining marks** (` ิ ี ึ ื ั ุ ู ฺ`) — แต่ละ mark จะกิน width 1 แทนที่จะเป็น 0 ทำให้ตารางภาษาไทย/บาลี drift

### ปัญหา

```text
+------------+------+-------+
|    ชื่อ     | ราคา | จำนวน |   ← ชื่อ + ื + ่ = width 3 ใน Discord
| ก๋วยเตี๋ยว |   45 |     3 |   ← ก๋วยเตี๋ยว + ๋ + ี + ๋ = width 11
+------------+------+-------+
         ↑ width 12 ใน wcwidth แต่ Discord render 13 → │ ขยับ!
```

`ก๋วยเตี๋ยว` len=10, wcwidth=7 → gap=3 (3 zero-width marks)

### Solution: `safe_width=True`

เมื่อเปิด safe_width โปรแกรมจะคำนวณ:

1. คำนวณ column width ด้วย `len()` แทน `wcwidth` (นับทุกตัวอักษรเป็น width 1)
2. เพิ่ม `gap = len_cell - wcwidth_cell` ให้ padded_lens (ชดเชย mark ที่ Platform render)
3. เพิ่ม buffer +1 สำหรับ font overhang

```text
+----------------+------+-------+
|      ชื่อ      | ราคา | จำนวน |   ← extra 4 spaces
| ก๋วยเตี๋ยว     |   45 |     3 |   ← gap(3) + buffer(1) = 4 extra
+----------------+------+-------+
```

### วิธีเรียกใช้

```json
{
  "headers": ["ชื่อ", "ราคา"],
  "rows": [["ก๋วยเตี๋ยว", "45"]],
  "fmt": "grid",
  "safe_width": true
}
```

หรือผ่าน Python API:

```python
from ascii_table_mcp.generate_table import render_ascii_grid
table = render_ascii_grid(rows, safe_width=True)
```

### อนาคต: Character Width Database

การคำนวณ width แบบ wcwidth หรือ len() ยัง approximation — อนาคตอาจสร้าง **ตาราง lookup ความกว้างจริงของอักขระไทยแต่ละตัว** สำหรับ platform/font หลักๆ (Discord, Terminal Windows, Terminal Linux) เพื่อให้ alignment แน่นอน 100%

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

## HTML Table for Discord/Telegram (fmt="html")

Discord และ Telegram **ไม่มี monospace font ที่รองรับภาษาไทยบน Windows** — ทำให้ `|` และ `│` ใน code block ดูโย้ไม่ตรงกัน

**วิธีแก้:** ใช้ `fmt="html"` เพื่อสร้าง HTML table ที่ browser จัด alignment ให้อัตโนมัติ แล้ว screenshot ส่งเป็นภาพ

![Dark](examples/ex_dark.png)

*ตัวอย่าง: `fmt="html"` style=dark (ค่าเริ่มต้น)*

4 styles ให้เลือก:

| Style | Preview | เหมาะกับ |
|-------|---------|---------|
| `dark` | ![dark](examples/ex_dark.png) | Discord/Telegram dark mode |
| `light` | ![light](examples/ex_light.png) | Document, PDF |
| `minimal` | ![minimal](examples/ex_minimal.png) | Blog, website |
| `compact` | ![compact](examples/ex_compact.png) | เนื้อหาเย็น, จอแคบ |

**การเรียกใช้:**

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [["กมฺม", "kamma", "นาม", "กรรม"]],
  "fmt": "html",
  "style": "dark"
}
```

---

## Grid Styles

10 styles จาก [ozh/ascii-tables](https://github.com/ozh/ascii-tables):

| Style | Top | Header sep | Data sep | Bottom | Notes |
|-------|-----|-----------|----------|--------|-------|
| `mysql` | `+--+` | `+--+` | `+--+` | `+--+` | default |
| `separated` | `+==+` | `+==+` | `+--+` | `+--+` | หัวตารางหนา |
| `compact` | none | ` --- ` | none | none | ไม่มีกรอบ |
| `gfm` | none | `\|--\|` | none | none | GitHub style |
| `reddit` | none | `--\|--` | none | none | Reddit style |
| `rounded` | `.--.` | `:+:` | none | `'--'` | มุมมน |
| `rst` | `+==+` | `+--+` | `+==+` | `+==+` | reStructuredText |
| `box` | `┌┬┐` | `├┼┤` | `├┼┤` | `└┴┘` | Unicode box |
| `unicode` | `╔╦╗` | `╠╬╣` | `╠╬╣` | `╚╩╝` | double-line |
| `dots` | `┌┬┐` | `├┼┤` | none | `└┴┘` | no row separators |

### Format Comparison

| Format | Example | เหมาะกับ |
|--------|---------|----------|
| `grid` | `+----+----+` | Default — terminal, code review, GitHub |
| `box` / `safe` | `┌────┬────┐` | presentation, formal doc |
| `pipe` | `\| \| \|` | Markdown |
| `grid` + `safe_width=True` | `+------+----+` | Discord, browser ที่ zero-width ≠ 0 |
| `html` | HTML `<table>` | Discord/Telegram ภาษาไทย — screenshot เป็นภาพ |

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
+-------+-----+
| ชื่อ    | อายุ |
+-------+-----+
| สมชาย | 30  |
| สมหญิง | 25  |
+-------+-----+
```

---

## Architecture

```text
ascii-table-mcp/
├── ascii_table_mcp/
│   ├── __init__.py      # MCP server (FastMCP)
│   ├── generate_table.py # Core rendering engine + render_html_table
│   └── thaiwidth.py     # Thai-aware display width
├── server.py            # Thin wrapper for `python server.py`
├── table_to_image.py    # HTML → screenshot helper
├── requirements.txt     # mcp + wcwidth
├── pyproject.toml        # uv / pip install
├── ascii-table-mcp.bat  # Windows wrapper
├── LICENSE              # MIT
└── README.md            # เอกสารนี้
```

Core rendering (`render_table`, `render_ascii_grid`, `render_pipe_table`, `render_table_safe`) อยู่ใน `generate_table.py` — server.py import มาใช้ ไม่มี code ซ้ำ

---

## Related

- [ozh/ascii-tables](https://github.com/ozh/ascii-tables) — ต้นแบบ table styles (mysql, separated, compact, gfm, reddit, rounded, rst, box, unicode, dots)
- [dmarsters/ascii-art-mcp](https://github.com/dmarsters/ascii-art-mcp) — decorative ASCII art (shaded boxes, styled tables)
- [schachmat/wego](https://github.com/schachmat/wego) — Go terminal weather app, uses go-runewidth (equivalent to our wcwidth)
- [akiomik/seaw](https://github.com/akiomik/seaw) — Scala port of wcwidth
- [wcwidth](https://pypi.org/project/wcwidth/) — Python port of wcwidth(3)

---

## License

MIT — แจกฟรี ใช้ได้ทั้งส่วนตัวและพาณิชย์
