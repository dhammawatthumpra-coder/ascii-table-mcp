# ASCII Table MCP Server

Unicode box-drawing table generator สำหรับ MCP-compatible agents.
ใช้ `wcwidth` จัดการความกว้างของตัวอักษร Thai/Pali/CJK ได้อย่างถูกต้อง

## Tools

### `make_table`
สร้างตารางจาก headers + rows

```python
make_table(
    headers=["ชื่อ", "ค่า", "หมายเหตุ"],
    rows=[
        ["กมฺม", "kamma", "บาลี"],
        ["อวิชฺชา", "avijjā", "กิเลส"],
    ]
)
```

### `make_table_from_csv`
parse CSV string แล้ว render

```python
make_table_from_csv(
    csv_text="ชื่อ,อายุ\\nสมชาย,30\\nสมหญิง,25",
    delimiter=",",
    has_header=True
)
```

### `make_table_preview`
แสดงตัวอย่างตาราง (Thai/Pali หรือ simple ASCII)

## การติดตั้ง

```bash
pip install -r requirements.txt
```

## การใช้งาน

### stdio mode (สำหรับ MCP)
```bash
python server.py
```

### HTTP mode (debugging)
```bash
python server.py --http
```

## ลงทะเบียนกับ Hermes

```bash
hermes mcp add ascii-table --command "python F:\\_Ai\\ascii-table-mcp\\server.py"
```

## Architecture

```
ascii-table-mcp/
├── server.py          # MCP server (FastMCP)
├── requirements.txt   # dependencies
└── README.md          # เอกสารนี้
```

- ใช้ `FastMCP` จาก official MCP Python SDK
- Render core (`render_table()`) ย้ายมาจาก `generate_table.py` ใน skill `tabular-ascii`
- Width handling: `wcwidth.wcswidth()` → fallback `len()`
