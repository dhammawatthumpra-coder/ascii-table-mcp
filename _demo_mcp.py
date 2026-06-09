"""Demo: render + analyze via MCP tools."""
import subprocess, json

proc = subprocess.Popen(
    ['python3', 'F:\\_Ai\\ascii-table-mcp\\server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

data = [
    ["คำบาลี",    "Roman",             "หมวด",   "ความหมาย"],
    ["กมฺม",      "kamma",             "นาม",    "กรรม"],
    ["กามจฺฉนฺท",  "kāmacchanda",       "นิวรณ์",  "ความพอใจในกาม"],
    ["อวิชฺชา",    "avijjā",            "กิเลส",   "ความไม่รู้"],
    ["ปฏิจจสมุปฺปาท", "paṭiccasamuppāda", "ธรรม",   "เหตุปัจจัยต่อเนื่อง"],
    ["ธมฺม",      "dhamma",            "ทั่วไป",  "ธรรม/คำสอน"],
    ["สติ",       "sati",              "เจตสิก",  "ความระลึกได้"],
]

msgs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}},
    {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"make_table","arguments":{"headers":data[0],"rows":data[1:],"format":"grid"}}},
    {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"make_table","arguments":{"headers":data[0],"rows":data[1:],"format":"box"}}},
]

payload = "\n".join(json.dumps(m) for m in msgs)
out, _ = proc.communicate(input=payload, timeout=5)
for line in out.strip().split("\n"):
    try:
        d = json.loads(line)
        if "result" in d and "content" in d["result"]:
            for c in d["result"]["content"]:
                if c["type"] == "text":
                    print(c["text"])
    except:
        pass
proc.terminate()
