import subprocess, json

proc = subprocess.Popen(
    ['python3', 'F:\\_Ai\\ascii-table-mcp\\server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

data = [["\u0e04\u0e33\u0e1a\u0e32\u0e25\u0e35","Roman","\u0e2b\u0e21\u0e27\u0e14"],
        ["\u0e01\u0e21\u0e4d\u0e21","kamma","\u0e19\u0e32\u0e21"],
        ["\u0e2d\u0e27\u0e34\u0e0a\u0e4d\u0e0a\u0e32","avijj\u0101","\u0e01\u0e34\u0e40\u0e25\u0e2a"]]

msgs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}},
    {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"make_table","arguments":{"headers":data[0],"rows":data[1:],"format":"box"}}},
    {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"make_table","arguments":{"headers":data[0],"rows":data[1:],"format":"safe"}}},
]

payload = "\n".join(json.dumps(m) for m in msgs)
out, _ = proc.communicate(input=payload, timeout=5)
label = "BOX"
for line in out.strip().split("\n"):
    try:
        d = json.loads(line)
        if "result" in d and "content" in d["result"]:
            for c in d["result"]["content"]:
                if c["type"] == "text":
                    print(f"=== {label} ===")
                    print(c["text"])
                    label = "SAFE"
    except:
        pass
proc.terminate()
