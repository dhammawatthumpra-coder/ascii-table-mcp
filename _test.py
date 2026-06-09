import subprocess, json

proc = subprocess.Popen(
    ['python3', 'F:\\_Ai\\ascii-table-mcp\\server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

msgs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}},
    {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"make_table","arguments":{"headers":["words","Roman","category"],"rows":[["kamma","kamma","noun"],["avijja","avijjaa","defilement"],["dhamma","dhamma","universal"]],"format":"grid"}}},
    {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"make_table","arguments":{"headers":["words","Roman","category"],"rows":[["kamma","kamma","noun"],["avijja","avijjaa","defilement"],["dhamma","dhamma","universal"]],"format":"box"}}},
]

payload = "\n".join(json.dumps(m) for m in msgs)
out, _ = proc.communicate(input=payload, timeout=5)
for line in out.strip().split("\n"):
    data = json.loads(line)
    if "result" in data and "content" in data["result"]:
        for c in data["result"]["content"]:
            if c["type"] == "text":
                print(c["text"])
                print("---")
proc.terminate()
