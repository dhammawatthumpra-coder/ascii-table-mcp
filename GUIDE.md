# คู่มือการใช้งาน ascii-table-mcp

ตารางภาษาไทย + โรมัน + ตัวเลข — alignment ตรงทุกแถว  
รองรับทั้ง code block ปกติ และส่งเป็นภาพสำหรับ Discord/Telegram

---

## สารบัญ

1. [ติดตั้ง](#1-ติดตั้ง)
2. [แบบ code block (terminal/GitHub/Discord ทั่วไป)](#2-แบบ-code-block)
3. [แบบภาพ (Discord โพสต์ภาษาไทย)](#3-แบบภาพ)
4. [ตัวอย่างการใช้งาน](#4-ตัวอย่าง)

---

## 1. ติดตั้ง

### pip

```bash
git clone https://github.com/dhammawatthumpra-coder/ascii-table-mcp.git
cd ascii-table-mcp
pip install -e .
```

### Register กับ Hermes

```bash
hermes mcp add ascii-table --command "python -m ascii_table_mcp"
```

### Register กับ Claude Desktop

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

---

## 2. แบบ code block

ใช้ได้ทุกที่ที่ render monospace font terminal, GitHub PR, Discord (ภาษาอังกฤษ/ตัวเลข)

| `fmt` | ลักษณะ | เหมาะกับ |
|-------|--------|----------|
| `"grid"` (default) | `+----+----+` | ทั่วไป, terminal, GitHub |
| `"box"` | `┌────┬────┐` | presentation, formal doc |
| `"pipe"` | `\| \| \|` | Markdown (.md files) |
| `"safe"` | box-drawing + len padding | Discord/browser ที่ zero-width ≠ 0 |
| `"minimal"` | ไม่มีกรอบ มีแต่ underline | กระทู้ Reddit, blog |

### ตัวอย่าง

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [
    ["กมฺม", "kamma", "นาม", "กรรม"],
    ["ญาณ", "ñāṇa", "ปัญญา", "ความรู้แจ้ง"],
    ["ก๋วยเตี๋ยว", "thai", "อาหาร", "noodle soup"]
  ],
  "fmt": "grid"
}
```

ผลลัพธ์:

```text
+---------------+---------------+---------+-------------------+
| คำบาลี        | Roman         | หมวด    | ความหมาย          |
+---------------+---------------+---------+-------------------+
| กมฺม          | kamma         | นาม     | กรรม              |
| ญาณ           | ñāṇa          | ปัญญา   | ความรู้แจ้ง       |
| ก๋วยเตี๋ยว    | thai          | อาหาร   | noodle soup       |
+---------------+---------------+---------+-------------------+
```

### safe_width

ถ้า Discord/browser render สระบน/ล่าง ( ิ ี ึ ื ั ุ ู) กว้างเกิน wcwidth ให้เปิด:

```json
{
  "headers": ["ชื่อ", "ราคา"],
  "rows": [["ก๋วยเตี๋ยว", "45"]],
  "fmt": "grid",
  "safe_width": true
}
```

---

## 3. แบบภาพ

สำหรับ **Discord/Telegram ที่มีภาษาไทย** —  
Windows ไม่มี monospace font ที่ support ภาษาไทย ทำให้ code block ดูโย้

### วิธีใช้

ใช้ `fmt="html"` แทน:

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [
    ["กมฺม", "kamma", "นาม", "กรรม"],
    ["ญาณ", "ñāṇa", "ปัญญา", "ความรู้แจ้ง"]
  ],
  "fmt": "html"
}
```

ผลลัพธ์ที่ได้คือ **HTML file path**:

```
HTML table saved to: F:\_Ai\ascii-table-mcp\_table_render.html
Open in browser with:
  browser_navigate(url='file:///F:/_Ai/ascii-table-mcp/_table_render.html')
Then screenshot with:
  browser_vision(question='verify table')
```

### Auto-workflow (สำหรับ Agent)

Agent จะทำอัตโนมัติเมื่อเจอ `fmt="html"`:

```
Agent → make_table(fmt="html", ...)
     ↓ สร้าง HTML file
     ↓ browser_navigate(url=...)
     ↓ browser_vision(question='verify')
     ↓ crop ด้วย Pillow
     ↓ MEDIA:<cropped_image>  → ส่งเป็นภาพใน Discord
```

### ตัวอย่างผลลัพธ์ (ภาพ)

![ตัวอย่างตารางภาษาไทย](https://i.imgur.com/placeholder.png)

**ข้อดีของแบบภาพ:**
- ✅ ภาษาไทยอ่านชัดเจน (ใช้ Noto Sans Thai)
- ✅ alignment ตรง — browser จัด column ให้อัตโนมัติ
- ✅ ใช้ offline ได้ (font ถูกแคช local)
- ✅ สี dark theme เข้ากับ Discord/Telegram

**ข้อควรรู้:**
- ต้องการ browser session (Hermes/Claude Desktop ต้องมี browser tool)
- font ~450KB (download ครั้งแรก แล้ว cache ไว้)
- ไม่เหมาะกับที่ไม่มี browser tool (CLI-only)

---

## 4. ตัวอย่าง

### 4.1 ตารางบาลี 4 คอลัมน์

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [
    ["ปฏิจจสมุปฺปาท", "paṭiccasamuppāda", "ธรรม", "เหตุปัจจัยต่อเนื่อง"],
    ["กามจฺฉนฺท", "kāmacchanda", "นิวรณ์", "ความพอใจในกาม"],
    ["อวิชฺชา", "avijjā", "กิเลส", "ความไม่รู้"]
  ],
  "fmt": "grid",
  "auto_format": false
}
```

### 4.2 ตารางตัวเลข (auto right-align)

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

### 4.3 ตารางภาษาไทยสำหรับ Discord (แบบภาพ)

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [
    ["กมฺม", "kamma", "นาม", "กรรม"],
    ["ญาณ", "ñāṇa", "ปัญญา", "ความรู้แจ้ง"],
    ["ก๋วยเตี๋ยว", "thai", "อาหาร", "noodle soup"]
  ],
  "fmt": "html"
}
```

Agent จะส่งภาพให้อัตโนมัติ

---

## Troubleshooting

**Q: ตารางใน Discord code block ยังโย้**
A: Discord code block ไม่มี monospace font ไทย → ใช้ `fmt="html"` + screenshot แทน

**Q: `fmt="html"` ไม่มี internet**
A: font ถูกดาวน์โหลดแคชไว้ที่ `image_cache/NotoSansThai_VF.ttf` ใช้ offline ได้

**Q: อยากให้ตารางเล็กลง / ใหญ่ขึ้น**
A: ปรับ `padding` ใน CSS ของ `render_html_table()`

**Q: ใช้กับ Telegram ได้ไหม**
A: ได้ — ส่งเป็นภาพ attachment เหมือน Discord

---

## Reference

- GitHub: https://github.com/dhammawatthumpra-coder/ascii-table-mcp
- รายงาน bug / suggestions: เปิด issue ที่ GitHub
- MCP tools: `make_table`, `make_table_from_csv`, `make_table_from_json`, `make_table_preview`, `debug_table`, `analyze_table`, `validate_table_text`
