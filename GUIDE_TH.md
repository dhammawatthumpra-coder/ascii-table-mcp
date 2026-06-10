# คู่มือการใช้งาน ASCII Table MCP

เครื่องมือสร้างตารางที่รองรับภาษาไทย บาลี และ CJK — ใช้ได้ทั้งแบบ Code Block และ HTML Image

---

## แบบที่ 1: Code Block (สำหรับ Terminal / GitHub)

ใช้ `fmt="grid"` กับ `safe_width=True`:

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [
    ["กมฺม", "kamma", "นาม", "กรรม"],
    ["ญาณ", "ñāṇa", "ปัญญา", "ความรู้แจ้ง"]
  ],
  "fmt": "grid",
  "safe_width": true
}
```

ผลลัพธ์:

```text
+----------+-------+---------+---------------+
| คำบาลี   | Roman | หมวด    | ความหมาย      |
+----------+-------+---------+---------------+
| กมฺม     | kamma | นาม     | กรรม          |
| ญาณ      | ñāṇa  | ปัญญา   | ความรู้แจ้ง   |
+----------+-------+---------+---------------+
```

**หมายเหตุ:** Code block ใช้ได้ดีบน GitHub, terminal, และ platform ที่มี monospace font รองรับภาษาไทย  
บน Discord/Telegram Windows ภาษาไทยอาจดูโย้เพราะไม่มี monospace font ไทย — ใช้ **แบบที่ 2** แทน

---

## แบบที่ 2: HTML + Screenshot (สำหรับ Discord / Telegram)

ใช้ `fmt="html"` เพื่อสร้างตารางด้วย Noto Sans Thai (Google Fonts) ที่ดูสวยงามทุก platform  
จากนั้น screenshot เป็นภาพ ส่งเป็น attachment

**ขั้นตอน:**

### 1. สร้าง HTML

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [
    ["กมฺม", "kamma", "นาม", "กรรม"],
    ["ญาณ", "ñāṇa", "ปัญญา", "ความรู้แจ้ง"],
    ["ก๋วยเตี๋ยว", "kuaytiaw", "อาหาร", "noodle soup"]
  ],
  "fmt": "html",
  "style": "dark"
}
```

### 2. เปิดใน Browser

```python
browser_navigate(url='file:///path/to/ascii-table-mcp/_table_render_dark.html')
```

### 3. Screenshot

```python
browser_vision(question='verify')
```
→ จะได้ screenshot path (ถึง vision ล่ม ไฟล์ก็ถูกบันทึก)

### 4. Crop (trim พื้นหลัง)

```python
from PIL import Image
img = Image.open(screenshot_path)
bg = (30, 30, 46)  # หรือ (255,255,255) ถ้า style=light
# crop อัตโนมัติ
img.crop((left, top, right, bottom)).save('table.png')
```

### 5. ส่งเป็นภาพ

```
MEDIA:table.png
```

---

## เปลี่ยน Style

| Style | Preview | ใช้กับ |
|-------|---------|-------|
| `dark` | ![dark](examples/ex_dark.png) | Discord/Telegram dark mode |
| `light` | ![light](examples/ex_light.png) | Document, PDF |
| `minimal` | ![minimal](examples/ex_minimal.png) | Blog, website |
| `compact` | ![compact](examples/ex_compact.png) | เนื้อหาเยอะ, จอแคบ |

```json
{ "fmt": "html", "style": "light" }
```

---

## เปลี่ยนตาราง (Grid sub-style)

ใช้กับ `fmt="grid"`:

| style | ลักษณะ |
|-------|--------|
| `mysql` (default) | `+--+--+` มาตรฐาน |
| `separated` | `+==+==+` หัวตารางหนา |
| `compact` | ไม่มีกรอบ |
| `gfm` | `|--|` แบบ GitHub |
| `box` / `unicode` | ┌─┬─┐ หรือ ╔═╦═╗ |

```json
{ "fmt": "grid", "style": "box" }
```

---

## Auto-Format

`auto_format=true` (default) → ตัวเลขชิดขวา, หัวตารางกึ่งกลาง

```json
{
  "headers": ["สินค้า", "ราคา", "จำนวน"],
  "rows": [["ก๋วยเตี๋ยว", "45", "3"], ["ข้าวผัด", "55", "2"]],
  "fmt": "grid",
  "auto_format": true
}
```

```text
+============+======+=======+
|   สินค้า    | ราคา | จำนวน |
+============+======+=======+
+------------+------+-------+
| ก๋วยเตี๋ยว |   45 |     3 |
+------------+------+-------+
| ข้าวผัด    |   55 |     2 |
+------------+------+-------+
```

---

## ไฟล์ประกอบ

| ไฟล์ | หน้าที่ |
|------|--------|
| `_table_render_*.html` | HTML สำหรับ screenshot |
| `NotoSansThai_VF.ttf` | ฟอนต์ไทย (local) |
| `table_to_image.py` | Helper สร้าง HTML |
| `examples/*.png` | รูปตัวอย่างสำหรับคู่มือ |
