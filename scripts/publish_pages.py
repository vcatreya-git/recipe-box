#!/usr/bin/env python3
"""Build a static GitHub Pages site: hub + prototype + product docs."""
from __future__ import annotations

import re
from pathlib import Path

import markdown

VAULT = Path(
    "/Users/venkatramanchandrasekar/Library/Mobile Documents/"
    "iCloud~md~obsidian/Documents/Thoughts/Projects/projectRecipeBox"
)
OUT = Path("/Users/venkatramanchandrasekar/projects/recipe-box/docs")

LINK_MAP = {
    "Design": "design.html",
    "Architecture": "architecture.html",
    "PRD": "prd.html",
    "Solution-Sketch": "sketch.html",
    "Solution Sketch": "sketch.html",
    "Design-Review-v1.6": "design-review.html",
    "Architecture-Review-v1.1": "architecture-review.html",
    "00-Decision-Log": "decisions.html",
    "00-Decision-Log.md": "decisions.html",
    "Challenge-Report": "prd.html",
}

PAGES = [
    ("design.html", "Design", "Design.md"),
    ("architecture.html", "Architecture", "Architecture.md"),
    ("prd.html", "PRD", "PRD.md"),
    ("sketch.html", "Solution Sketch", "Solution-Sketch.md"),
    ("design-review.html", "Design review", "Design-Review-v1.6.md"),
    ("architecture-review.html", "Architecture review", "Architecture-Review-v1.1.md"),
    ("decisions.html", "Decisions", "00-Decision-Log.md"),
]

NAV = [
    ("index.html", "Home"),
    ("prototype.html", "Prototype"),
    ("design.html", "Design"),
    ("architecture.html", "Architecture"),
    ("prd.html", "PRD"),
    ("sketch.html", "Sketch"),
    ("design-review.html", "Design review"),
    ("architecture-review.html", "Arch review"),
    ("decisions.html", "Decisions"),
]

CSS = """
:root{
  --bg:#F7F1E6; --surface:#FFFCF5; --title:#2A2118; --text:#3D342A;
  --muted:#7A7064; --line:#E4D9C6; --primary:#B5533C; --primaryInk:#FFF8F0;
  --accentSoft:#F3E7C4;
}
*{box-sizing:border-box}
html,body{margin:0;background:#20211E;color:var(--text)}
body{font-family:Inter,-apple-system,Segoe UI,Roboto,Helvetica,sans-serif;
  display:flex;justify-content:center;min-height:100vh}
.wrap{width:100%;max-width:920px;min-height:100vh;background:var(--bg);
  border-left:1px solid #111;border-right:1px solid #111}
header{position:sticky;top:0;z-index:5;background:var(--bg);
  border-bottom:1px solid var(--line);padding:14px 20px 10px}
.brand{font-family:Georgia,"Iowan Old Style",serif;font-size:22px;font-weight:600;
  color:var(--title);margin:0 0 8px;letter-spacing:-.02em}
.brand a{color:inherit;text-decoration:none}
nav{display:flex;flex-wrap:wrap;gap:6px}
nav a{font-size:12.5px;font-weight:650;color:var(--text);text-decoration:none;
  border:1px solid var(--line);background:var(--surface);border-radius:999px;
  padding:6px 11px}
nav a.on,nav a:hover{background:var(--title);color:var(--bg);border-color:var(--title)}
main{padding:22px 22px 64px;line-height:1.6;font-size:16px}
h1,h2,h3,h4{font-family:Georgia,"Iowan Old Style",serif;color:var(--title);
  line-height:1.25;letter-spacing:-.02em}
h1{font-size:28px;margin:8px 0 14px}
h2{font-size:22px;margin:28px 0 10px;padding-top:8px;border-top:1px solid var(--line)}
h3{font-size:18px;margin:22px 0 8px}
p,li{color:var(--text)}
a{color:var(--primary)}
blockquote{margin:12px 0;padding:10px 14px;background:var(--accentSoft);
  border-left:3px solid var(--primary);color:var(--title)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em;
  background:#efe6d4;padding:1px 5px;border-radius:5px}
pre{background:#2A2118;color:#FFF8F0;padding:14px 16px;border-radius:12px;
  overflow:auto;font-size:13px;line-height:1.45}
pre code{background:none;color:inherit;padding:0}
table{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0 18px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:var(--surface);color:var(--title)}
.hero{background:var(--title);color:#FFFCF5;border-radius:16px;padding:22px 22px 20px;margin:0 0 22px}
.hero h1{color:#FFFCF5;margin:0 0 8px}
.hero p{color:rgba(255,252,245,.82);margin:0 0 14px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.card{display:block;background:var(--surface);border:1px solid var(--line);
  border-radius:14px;padding:14px 16px;text-decoration:none;color:inherit}
.card b{display:block;font-size:16px;color:var(--title);margin-bottom:4px}
.card span{font-size:13px;color:var(--muted);line-height:1.45}
.card.primary{background:var(--primary);color:var(--primaryInk);border-color:transparent}
.card.primary b,.card.primary span{color:var(--primaryInk)}
.note{font-size:13px;color:var(--muted)}
"""

def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def wiki_to_md(text: str) -> str:
    def repl(m: re.Match) -> str:
        raw = m.group(1).strip()
        if "|" in raw:
            target, label = raw.split("|", 1)
        else:
            target, label = raw, raw
        target = target.strip()
        label = label.strip()
        href = LINK_MAP.get(target)
        if not href:
            base = target.split("/")[-1]
            href = LINK_MAP.get(base)
        if href:
            return f"[{label}]({href})"
        return label

    return re.sub(r"\[\[([^\]]+)\]\]", repl, text)


def nav_html(current: str) -> str:
    bits = []
    for href, label in NAV:
        cls = " on" if href == current else ""
        bits.append(f'<a class="{cls.strip()}" href="{href}">{label}</a>')
    return "".join(bits)


def page(title: str, body: str, current: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Recipe Box</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@450;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
{extra_head}
</head>
<body>
<div class="wrap">
<header>
  <p class="brand"><a href="index.html">Recipe Box</a></p>
  <nav>{nav_html(current)}</nav>
</header>
<main>
{body}
</main>
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{startOnLoad:false, theme:"neutral"}});
document.querySelectorAll("pre code.language-mermaid").forEach(function(el){{
  var pre = el.parentElement;
  var div = document.createElement("div");
  div.className = "mermaid";
  div.textContent = el.textContent;
  pre.replaceWith(div);
}});
mermaid.run();
</script>
</body>
</html>
"""


def convert_md(src: Path) -> str:
    raw = strip_frontmatter(src.read_text(encoding="utf-8"))
    raw = wiki_to_md(raw)
    return markdown.markdown(
        raw,
        extensions=["extra", "sane_lists", "toc", "nl2br", "fenced_code", "tables"],
    )


def write_hub() -> None:
    body = """
<div class="hero">
  <h1>Recipe Box</h1>
  <p>Click-through prototype and the product docs. This is not the production app, and it is not on the GitHub profile.</p>
  <a class="card primary" href="prototype.html" style="display:inline-block;max-width:280px">
    <b>Open the prototype</b>
    <span>Interactive freeze — start with “load populated demo”.</span>
  </a>
</div>
<div class="cards">
  <a class="card" href="design.html"><b>Design</b><span>v1.6 screens, flows, Browse / generate as the user sees them.</span></a>
  <a class="card" href="architecture.html"><b>Architecture</b><span>v1.1 — how home loads, fillWeek, extract tools. Draft; hosting unlocked.</span></a>
  <a class="card" href="prd.html"><b>PRD</b><span>Product requirements.</span></a>
  <a class="card" href="sketch.html"><b>Solution sketch</b><span>Entities and contracts through delta #15.</span></a>
  <a class="card" href="design-review.html"><b>Design review</b><span>Approved with changes.</span></a>
  <a class="card" href="architecture-review.html"><b>Architecture review</b><span>Needs rework before build.</span></a>
  <a class="card" href="decisions.html"><b>Decisions</b><span>Logged product and stack calls.</span></a>
</div>
<p class="note" style="margin-top:22px">Source of the click-through is Prototype-v2.html. Reviews are not a ship signal — hosting is still unlocked.</p>
"""
    (OUT / "index.html").write_text(page("Home", body, "index.html"), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    proto = VAULT / "Prototype-v2.html"
    (OUT / "prototype.html").write_text(proto.read_text(encoding="utf-8"), encoding="utf-8")
    assets_src = VAULT / "prototype-assets"
    assets_dst = OUT / "prototype-assets"
    assets_dst.mkdir(exist_ok=True)
    for img in assets_src.glob("*.jpg"):
        dest = assets_dst / img.name
        dest.write_bytes(img.read_bytes())

    write_hub()
    md = markdown.Markdown(
        extensions=["extra", "sane_lists", "toc", "nl2br", "fenced_code", "tables"]
    )
    for dest, title, src_name in PAGES:
        html = convert_md(VAULT / src_name)
        # reset extension state between files
        md.reset()
        (OUT / dest).write_text(page(title, html, dest), encoding="utf-8")
        print("wrote", dest)


if __name__ == "__main__":
    main()
