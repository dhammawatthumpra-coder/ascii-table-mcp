# คู่มือการใช้งาน ASCII Table MCP

เครื่องมือสร้างตารางที่รองรับภาษาไทย บาลี และ CJK — ใช้ได้ทั้งแบบ Code Block, PNG Image, และ SVG Vector

---

## แบบที่ 1: Code Block (สำหรับ Terminal / GitHub / Discord)

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

**หมายเหตุ:** Code block บน Discord Windows อาจดูโย้เพราะไม่มี monospace font ไทย — ใช้ **แบบที่ 2** แทน

---

## แบบที่ 2: Export PNG โดยตรง (ส่งเข้าฟีดทันที)

ใช้ `export_png` — สร้าง PNG crop อัตโนมัติ ไม่ต้องเปิด browser หรือ crop เอง

```json
{
  "headers": ["คำบาลี", "Roman", "หมวด", "ความหมาย"],
  "rows": [
    ["กมฺม", "kamma", "นาม", "กรรม"],
    ["ญาณ", "ñāṇa", "ปัญญา", "ความรู้แจ้ง"],
    ["ก๋วยเตี๋ยว", "kuaytiaw", "อาหาร", "noodle soup"]
  ],
  "style": "dark"
}
```

MCP คืน path ไฟล์ PNG — ส่งด้วย `MEDIA:<path>` ได้ทันที

**4 styles:**

| style | ลักษณะ |
|-------|--------|
| `dark` (default) | พื้นหลังดำ, ตัวอักษรขาว |
| `light` | พื้นหลังขาว, ตัวอักษรดำ |
| `minimal` | กรอบบาง, โปร่งใส |
| `compact` | แบบกระชับ, padding น้อย |

---

## แบบที่ 3: Export SVG (Vector — ซูมได้, Embed ได้)

ใช้ `export_svg` — SVG ใช้ foreignObject + Noto Sans Thai

```json
{
  "headers": ["คำบาลี", "Roman"],
  "rows": [["กมฺม", "kamma"], ["อวิชฺชา", "avijjā"]],
  "style": "dark"
}
```

SVG คมชัดทุกขนาด (ซูมเท่าไรก็ไม่แตก), embed ในเว็บหรือเอกสาร PDF ได้

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
