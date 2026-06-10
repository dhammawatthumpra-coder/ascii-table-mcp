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

**Note:** Code blocks work well on GitHub, terminals, and platforms with proper monospace Thai fonts.  \nOn Discord/Telegram (Windows), Thai monospace rendering is broken — use **Mode 2** instead.

---

## Mode 2: Direct PNG Export (One Step)

Use `export_png` — generates cropped PNG via headless Playwright. No browser, no manual screenshot, no crop step.

```json
{
  "headers": ["Pali", "Roman", "Type", "Meaning"],
  "rows": [
    ["กมฺม", "kamma", "Noun", "action"],
    ["ญาณ", "ñāṇa", "Wisdom", "direct knowing"],
    ["ก๋วยเตี๋ยว", "kuaytiaw", "Food", "noodle soup"]
  ],
  "style": "dark"
}
```

Returns: path to cropped PNG file. Send with `MEDIA:<path>`.

**4 styles:**

| style | Appearance |
|-------|-----------|
| `dark` (default) | Dark background, white text |
| `light` | Light background, dark text |
| `minimal` | Thin borders, transparent |
| `compact` | Small padding, dense |

---

## Mode 3: SVG Export (Vector — Zoomable, Embeddable)

Use `export_svg` for vector output. Uses foreignObject + Noto Sans Thai.

```json
{
  "headers": ["Pali", "Roman"],
  "rows": [["กมฺม", "kamma"], ["อวิชฺชา", "avijjā"]],
  "style": "dark"
}
```

SVG stays sharp at any zoom level, embeddable in web pages and PDFs.

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
