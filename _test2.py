"""Test analyze_table with properly rendered grid table."""
import subprocess, json, sys

sys.path.insert(0, r'F:\_Ai\ascii-table-mcp')
from generate_table import render_ascii_grid

# Render a properly aligned grid table
rendered = render_ascii_grid([
    ["คำบาลี", "Roman", "หมวด"],
    ["กมฺม", "kamma", "นาม"],
    ["อวิชฺชา", "avijjā", "กิเลส"],
])

print("=== Table ===")
print(rendered)
print()

# Now test via MCP
proc = subprocess.Popen(
    ['python3', 'F:\\_Ai\\ascii-table-mcp\\server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

msgs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}},
    {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"analyze_table","arguments":{"table_text":rendered}}},
]

payload = "\n".join(json.dumps(m) for m in msgs)
out, _ = proc.communicate(input=payload, timeout=5)
for line in out.strip().split("\n"):
    try:
        data = json.loads(line)
        if "result" in data and "content" in data["result"]:
            for c in data["result"]["content"]:
                if c["type"] == "text":
                    print(c["text"])
    except:
        pass
proc.terminate()
