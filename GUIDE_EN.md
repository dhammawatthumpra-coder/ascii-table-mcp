# ASCII Table MCP — Usage Guide

Create tables that work in **code blocks** (terminal/GitHub) **and as beautiful images** (Discord/Slack/Telegram) — with proper Thai, Pali, CJK, and emoji alignment.

---

## Mode 1: Code Block (Terminal / GitHub / Code Review)

Use `fmt="grid"` with `safe_width=True` for platforms where combining marks render wider than zero:

```json
{
  "headers": ["Pali", "Roman", "Type", "Meaning"],
  "rows": [
    ["กมฺม", "kamma", "Noun", "action"],
    ["ญาณ", "ñāṇa", "Wisdom", "direct knowing"]
  ],
  "fmt": "grid",
  "safe_width": true
}
```

Output:

```text
+----------+-------+---------+----------------+
| Pali     | Roman | Type    | Meaning        |
+----------+-------+---------+----------------+
| กมฺม     | kamma | Noun    | action         |
| ญาณ      | ñāṇa  | Wisdom  | direct knowing |
+----------+-------+---------+----------------+
```

**Note:** Code blocks work well on GitHub, terminals, and platforms with proper monospace Thai fonts.  
On Discord/Telegram (Windows), Thai monospace rendering is broken — use **Mode 2** instead.

---

## Mode 2: HTML Screenshot (Discord / Telegram / Slack)

Use `fmt="html"` to render a table with Noto Sans Thai (perfect rendering everywhere).  
Then open the HTML in a browser and screenshot it.

### Step 1: Generate HTML

```json
{
  "headers": ["Pali", "Roman", "Type", "Meaning"],
  "rows": [
    ["กมฺม", "kamma", "Noun", "action"],
    ["ญาณ", "ñāṇa", "Wisdom", "direct knowing"],
    ["ก๋วยเตี๋ยว", "kuaytiaw", "Food", "noodle soup"]
  ],
  "fmt": "html",
  "style": "dark"
}
```

### Step 2: Open in Browser

```python
# The MCP server prints the file path — use it here:
browser_navigate(url='file:///path/to/ascii-table-mcp/_table_render_dark.html')
```

Or just open the generated `.html` file manually in your browser.

### Step 3: Screenshot

```python
browser_vision(question='verify')
```

→ Returns a screenshot path (even if vision analysis fails, the screenshot is saved).

### Step 4: Crop (trim background)

```python
from PIL import Image

img = Image.open(screenshot_path)
bg = (30, 30, 46)       # dark theme background
# or bg = (255, 255, 255) for light theme

pixels = img.load()
w, h = img.size
left, right, top, bottom = w, 0, h, 0
for y in range(h):
    for x in range(w):
        r, g, b = pixels[x, y][:3]
        if (r, g, b) != bg:
            if x < left:   left = x
            if x > right:  right = x
            if y < top:    top = y
            if y > bottom: bottom = y

pad = 10
left   = max(0, left - pad)
right  = min(w - 1, right + pad)
top    = max(0, top - pad)
bottom = min(h - 1, bottom + pad)

cropped = img.crop((left, top, right + 1, bottom + 1))
cropped.save('table.png')
```

Or use the included helper:

```bash
python table_to_image.py "Pali,Roman" "กมฺม,kamma"
```

### Step 5: Send as Image

```
MEDIA:table.png
```

---

## Choosing a Style

| Style | Preview | Best for |
|-------|---------|----------|
| `dark` | ![dark](examples/ex_dark.png) | Discord / Telegram dark mode |
| `light` | ![light](examples/ex_light.png) | Documentation, PDF |
| `minimal` | ![minimal](examples/ex_minimal.png) | Blog posts, websites |
| `compact` | ![compact](examples/ex_compact.png) | Dense data, narrow screens |

```json
{ "fmt": "html", "style": "light" }
```

---

## Grid Sub-Styles (for `fmt="grid"`)

| style | Appearance |
|-------|-----------|
| `mysql` (default) | `+--+--+` standard |
| `separated` | `+==+==+` bold header separator |
| `compact` | frameless |
| `gfm` | `\|--\|` GitHub style |
| `box` / `unicode` | ┌─┬─┐ or ╔═╦═╗ |

```json
{ "fmt": "grid", "style": "box" }
```

---

## Auto-Format

`auto_format=true` (default) → numbers right-aligned, headers centered.

```json
{
  "headers": ["Product", "Price", "Qty"],
  "rows": [["Noodle Soup", "45", "3"], ["Fried Rice", "55", "2"]],
  "fmt": "grid",
  "auto_format": true
}
```

```text
+============+======+=======+
|  Product   | Price |  Qty  |
+============+======+=======+
+------------+------+-------+
| Noodle Soup |   45 |     3 |
+------------+------+-------+
| Fried Rice  |   55 |     2 |
+------------+------+-------+
```

---

## Included Files

| File | Purpose |
|------|---------|
| `_table_render_*.html` | Generated HTML for screenshot (gitignored) |
| `table_to_image.py` | CLI helper for HTML → cropped PNG |
| `examples/*.png` | Preview images for documentation |

---

## Tips

- **Dark mode conversations** → use `style: "dark"` (default)
- **Docs / blog** → use `style: "light"` with `fmt: "html"`
- **Quick terminal tables** → `fmt: "grid"` with `safe_width: true`
- **Comparing editions** → `fmt: "html"`, `style: "compact"` for dense data
