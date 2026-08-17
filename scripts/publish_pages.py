#!/usr/bin/env python3
"""Publish Recipe Box docs/prototype using the PM Rocket docs-site pattern."""
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
}

DOC_PAGES = [
    ("design.html", "design.md", "Design", "v1.6 · draft", "Design.md"),
    ("architecture.html", "architecture.md", "Architecture", "v1.1 · draft", "Architecture.md"),
    ("prd.html", "PRD.md", "PRD", "approved with changes", "PRD.md"),
    ("sketch.html", "solution-sketch.md", "Solution Sketch", "delta #15", "Solution-Sketch.md"),
    ("design-review.html", None, "Design review", "approved with changes", "Design-Review-v1.6.md"),
    ("architecture-review.html", None, "Architecture review", "needs rework", "Architecture-Review-v1.1.md"),
    ("decisions.html", "decision-log.md", "Decision log", "living", "00-Decision-Log.md"),
]

TOP_LINKS = [
    ("index.html", "Home"),
    ("prd.html", "PRD"),
    ("design.html", "Design"),
    ("architecture.html", "Architecture"),
    ("prototype.html", "Prototype ↗"),
]

CHROME_CSS = r"""
:root {
  --primary: #B5533C;
  --primary-dark: #8E3E2C;
  --primary-light: #F3E7C4;
  --bg: #f8fafc;
  --card: #ffffff;
  --text: #1e293b;
  --subtext: #64748b;
  --border: #e2e8f0;
  --code-bg: #f1f5f9;
  --sidebar-w: 248px;
  --nav-h: 60px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; font-size: 15px; }
.topnav { position: fixed; top: 0; left: 0; right: 0; height: var(--nav-h); background: var(--card); border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 24px; gap: 24px; z-index: 100; }
.topnav-logo { font-weight: 700; font-size: 16px; color: var(--primary); text-decoration: none; }
.topnav-meta { font-size: 12px; color: var(--subtext); }
.topnav-links { margin-left: auto; display: flex; gap: 18px; flex-wrap: wrap; }
.topnav-links a { font-size: 13px; color: var(--subtext); text-decoration: none; font-weight: 500; }
.topnav-links a:hover, .topnav-links a.on { color: var(--primary); }
.layout { display: flex; padding-top: var(--nav-h); min-height: 100vh; }
.sidebar { width: var(--sidebar-w); flex-shrink: 0; padding: 32px 0 32px 16px; position: sticky; top: var(--nav-h); height: calc(100vh - var(--nav-h)); overflow-y: auto; border-right: 1px solid var(--border); background: var(--card); }
.sidebar-heading { font-size: 10px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: var(--subtext); margin: 16px 0 8px; padding-left: 12px; }
.sidebar a { display: block; font-size: 13px; color: var(--subtext); text-decoration: none; padding: 5px 12px; border-radius: 6px; margin-bottom: 2px; }
.sidebar a:hover, .sidebar a.on { color: var(--primary-dark); background: var(--primary-light); }
.main { flex: 1; padding: 40px 48px 80px; max-width: 900px; }
.doc-header { margin-bottom: 32px; }
.doc-header h1 { font-size: 30px; font-weight: 800; margin-bottom: 8px; line-height: 1.2; }
.doc-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.doc-meta span { font-size: 12px; color: var(--subtext); background: #f1f5f9; padding: 4px 10px; border-radius: 100px; }
h2 { font-size: 20px; font-weight: 700; color: var(--primary-dark); margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--primary-light); }
h3 { font-size: 16px; font-weight: 700; margin: 22px 0 8px; }
h4 { font-size: 13px; font-weight: 700; color: var(--subtext); margin: 16px 0 8px; }
p, li { margin-bottom: 10px; }
ul, ol { padding-left: 22px; margin-bottom: 14px; }
a { color: var(--primary); }
blockquote { border-left: 3px solid var(--primary); background: var(--primary-light); padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 16px 0; }
.table-wrap { overflow-x: auto; margin: 14px 0 20px; border-radius: 8px; border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
th { background: #f1f5f9; text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--border); }
td { padding: 9px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
pre { background: #0f172a; color: #e2e8f0; padding: 18px 20px; border-radius: 10px; overflow-x: auto; font-size: 12.5px; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
p code, li code, td code { background: var(--code-bg); color: var(--primary-dark); padding: 2px 6px; border-radius: 4px; font-size: 12.5px; }
pre code { background: none; color: inherit; padding: 0; }
.callout { border-left: 3px solid var(--primary); background: var(--primary-light); padding: 14px 18px; border-radius: 0 8px 8px 0; margin: 16px 0; font-size: 13.5px; }
@media (max-width: 900px) {
  .sidebar { display: none; }
  .main { padding: 24px 20px 60px; }
}
"""


def slug(text: str) -> str:
    s = re.sub(r"<[^>]+>", "", text)
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[-\s]+", "-", s)


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def wiki_to_md(text: str) -> str:
    def repl(m: re.Match) -> str:
        raw = m.group(1).strip()
        target, label = (raw.split("|", 1) + [raw])[:2] if "|" in raw else (raw, raw)
        target, label = target.strip(), label.strip()
        href = LINK_MAP.get(target) or LINK_MAP.get(target.split("/")[-1])
        return f"[{label}]({href})" if href else label

    return re.sub(r"\[\[([^\]]+)\]\]", repl, text)


def md_for_repo(text: str) -> str:
    """Wiki links → relative .html for the published md copies."""
    return wiki_to_md(strip_frontmatter(text))


def convert(src: Path) -> tuple[str, list[tuple[str, str]]]:
    raw = wiki_to_md(strip_frontmatter(src.read_text(encoding="utf-8")))
    html = markdown.markdown(
        raw,
        extensions=["extra", "sane_lists", "toc", "fenced_code", "tables"],
    )
    html = re.sub(
        r"<table>",
        '<div class="table-wrap"><table>',
        html,
    )
    html = re.sub(r"</table>", "</table></div>", html)
    toc = []

    def add_id(m: re.Match) -> str:
        level, inner = m.group(1), m.group(2)
        sid = slug(inner)
        if level == "2":
            toc.append((sid, re.sub(r"<[^>]+>", "", inner)))
        return f'<h{level} id="{sid}">{inner}</h{level}>'

    html = re.sub(r"<h([23])>(.*?)</h\1>", add_id, html, flags=re.S)
    return html, toc


def topnav(current_label: str) -> str:
    links = []
    for href, label in TOP_LINKS:
        cls = ' class="on"' if label.split()[0].lower() in current_label.lower() else ""
        extra = ' target="_blank"' if "Prototype" in label else ""
        links.append(f'<a href="{href}"{cls}{extra}>{label}</a>')
    return f"""<nav class="topnav">
  <a href="index.html" class="topnav-logo">Recipe Box</a>
  <span class="topnav-meta">/ {current_label}</span>
  <div class="topnav-links">{"".join(links)}
    <a href="https://github.com/vcatreya-git/recipe-box" target="_blank">GitHub ↗</a>
  </div>
</nav>"""


def sidebar(toc: list[tuple[str, str]], extra: str = "") -> str:
    items = "".join(f'<a href="#{sid}">{label}</a>' for sid, label in toc)
    return f"""<aside class="sidebar">
  <div class="sidebar-heading">On this page</div>
  {items or '<span style="padding:0 12px;font-size:12px;color:var(--subtext)">—</span>'}
  <div class="sidebar-heading">Docs</div>
  <a href="index.html">Home</a>
  <a href="prd.html">PRD</a>
  <a href="design.html">Design</a>
  <a href="architecture.html">Architecture</a>
  <a href="sketch.html">Solution sketch</a>
  <a href="design-review.html">Design review</a>
  <a href="architecture-review.html">Architecture review</a>
  <a href="decisions.html">Decisions</a>
  {extra}
</aside>"""


def wrap_doc(title: str, meta: str, body: str, toc: list[tuple[str, str]]) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Recipe Box</title>
<style>{CHROME_CSS}</style>
</head>
<body>
{topnav(title)}
<div class="layout">
{sidebar(toc)}
<main class="main">
  <div class="doc-header">
    <h1>{title}</h1>
    <div class="doc-meta"><span>{meta}</span><span>Recipe Box</span></div>
  </div>
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


INDEX = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Recipe Box — Capture, keep, cook</title>
<style>
:root {
  --teal: #B5533C;
  --teal-dark: #8E3E2C;
  --teal-light: #F3E7C4;
  --teal-xlight: #FFF8F0;
  --slate-900: #0f172a;
  --slate-800: #1e293b;
  --slate-700: #334155;
  --slate-600: #475569;
  --slate-500: #64748b;
  --slate-400: #94a3b8;
  --slate-200: #e2e8f0;
  --slate-100: #f1f5f9;
  --slate-50: #f8fafc;
  --white: #ffffff;
  --sidebar-w: 224px;
  --radius: 10px;
  --radius-sm: 6px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--white);color:var(--slate-800);line-height:1.6;font-size:15px;padding-left:var(--sidebar-w)}
a{color:var(--teal);text-decoration:none}
a:hover{text-decoration:underline}
.sidebar{position:fixed;top:0;left:0;bottom:0;width:var(--sidebar-w);background:var(--white);border-right:1px solid var(--slate-200);z-index:200;display:flex;flex-direction:column;overflow-y:auto}
.sb-logo{padding:16px 14px 12px;border-bottom:1px solid var(--slate-200)}
.sb-logo .wordmark{font-size:16px;font-weight:800;color:var(--slate-900);letter-spacing:-.3px}
.sb-status{display:inline-flex;align-items:center;gap:4px;margin-top:5px;font-size:10px;font-weight:600;color:var(--teal-dark);background:var(--teal-light);padding:2px 8px;border-radius:100px}
.sb-dot{width:5px;height:5px;border-radius:50%;background:var(--teal)}
.sb-group-label{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--slate-400);padding:12px 14px 3px}
.sb-nav{padding:4px 6px;flex:1}
.sb-nav a{display:flex;align-items:center;gap:7px;padding:6px 8px;font-size:12.5px;font-weight:500;color:var(--slate-500);border-radius:var(--radius-sm);text-decoration:none;margin-bottom:1px}
.sb-nav a:hover{background:var(--slate-100);color:var(--slate-800)}
.sb-nav a.active{background:var(--teal-xlight);color:var(--teal-dark);font-weight:600}
.sb-ctas{padding:10px;border-top:1px solid var(--slate-200)}
.sb-ctas a{display:block;text-align:center;padding:7px;font-size:12.5px;font-weight:600;border-radius:var(--radius-sm);text-decoration:none;margin-bottom:5px}
.sb-btn-primary{background:var(--teal);color:white}
.sb-btn-ghost{color:var(--slate-600);border:1px solid var(--slate-200)}
.section{padding:72px 40px}
.container{max-width:1020px;margin:0 auto}
.section-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--teal);margin-bottom:6px}
.section-title{font-size:clamp(20px,2.5vw,30px);font-weight:800;color:var(--slate-900);letter-spacing:-.6px;margin-bottom:8px}
.section-sub{font-size:14px;color:var(--slate-500);max-width:640px;margin-bottom:32px;line-height:1.65}
#overview{background:linear-gradient(155deg,var(--teal-xlight) 0%,var(--white) 55%);padding:80px 40px 72px;text-align:center}
.hero-badge{display:inline-flex;align-items:center;gap:5px;background:var(--teal-light);color:var(--teal-dark);font-size:11px;font-weight:600;padding:4px 13px;border-radius:100px;margin-bottom:20px}
#overview h1{font-size:clamp(26px,3.8vw,44px);font-weight:800;color:var(--slate-900);letter-spacing:-1.5px;line-height:1.1;max-width:680px;margin:0 auto 16px}
#overview h1 span{color:var(--teal)}
#overview .hero-sub{font-size:clamp(13px,1.6vw,16px);color:var(--slate-600);max-width:600px;margin:0 auto 28px;line-height:1.7}
.hero-ctas{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:5px;padding:10px 20px;border-radius:var(--radius);font-size:13px;font-weight:600;text-decoration:none}
.btn-primary{background:var(--teal);color:white}
.btn-secondary{background:white;color:var(--slate-800);border:1.5px solid var(--slate-200)}
#stats{background:var(--slate-900);padding:36px 40px}
.stats-grid{max-width:1020px;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,.08)}
.stat-item{background:var(--slate-900);padding:22px;text-align:center}
.stat-number{font-size:clamp(18px,2.4vw,26px);font-weight:800;color:var(--teal);display:block;margin-bottom:6px}
.stat-label{font-size:12px;color:rgba(255,255,255,.5);line-height:1.45}
.doc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.doc-card{display:block;background:white;border:1.5px solid var(--slate-200);border-radius:var(--radius);padding:18px;text-decoration:none;color:inherit}
.doc-card:hover{border-color:var(--teal)}
.doc-card b{display:block;font-size:14px;color:var(--slate-900);margin-bottom:4px}
.doc-card span{font-size:13px;color:var(--slate-500);line-height:1.5}
.section-alt{background:var(--slate-50)}
@media(max-width:800px){
  body{padding-left:0}
  .sidebar{display:none}
  .section,#overview{padding:48px 20px}
}
</style>
</head>
<body>
<aside class="sidebar">
  <div class="sb-logo">
    <div class="wordmark">Recipe Box</div>
    <div class="sb-status"><span class="sb-dot"></span>Prototype freeze · Aug 2026</div>
  </div>
  <nav class="sb-nav">
    <div class="sb-group-label">Product</div>
    <a href="#overview" class="active">Overview</a>
    <a href="#problem">The problem</a>
    <a href="#how">How it works</a>
    <div class="sb-group-label">Documentation</div>
    <a href="prd.html">PRD</a>
    <a href="design.html">Design</a>
    <a href="architecture.html">Architecture</a>
    <a href="sketch.html">Solution sketch</a>
    <a href="decisions.html">Decisions</a>
    <div class="sb-group-label">Reviews</div>
    <a href="design-review.html">Design review</a>
    <a href="architecture-review.html">Architecture review</a>
  </nav>
  <div class="sb-ctas">
    <a href="prototype.html" class="sb-btn-primary">View prototype</a>
    <a href="https://github.com/vcatreya-git/recipe-box" class="sb-btn-ghost">GitHub</a>
  </div>
</aside>

<section id="overview">
  <div class="hero-badge">Click-through freeze · not on the profile site</div>
  <h1>The Spotify of recipes.<br>Capture. Keep. <span>Cook.</span></h1>
  <p class="hero-sub">A personal library, a global catalogue, and a week generated from what you actually cook — not another bookmark graveyard.</p>
  <div class="hero-ctas">
    <a href="prototype.html" class="btn btn-primary">View prototype →</a>
    <a href="design.html" class="btn btn-secondary">Read the design</a>
  </div>
</section>

<div id="stats">
  <div class="stats-grid">
    <div class="stat-item"><span class="stat-number">4 tabs</span><div class="stat-label">Browse · My recipes · This Week · Profile</div></div>
    <div class="stat-item"><span class="stat-number">Draft → shop</span><div class="stat-label">Generate fills a draft; shopping list commits the week</div></div>
    <div class="stat-item"><span class="stat-number">No LLM menu</span><div class="stat-label">fillWeek is deterministic; extract uses schema.org then grok</div></div>
  </div>
</div>

<section id="problem" class="section">
  <div class="container">
    <div class="section-label">The problem</div>
    <h2 class="section-title">Saved is not cooked.</h2>
    <p class="section-sub">Recipes live in screenshots, reels, and ten apps. Planning a week still means a blank note. Recipe Box is a playlist for food: a catalogue anyone can browse, a box that is yours, a week generated from that box.</p>
  </div>
</section>

<section id="how" class="section section-alt">
  <div class="container">
    <div class="section-label">How it works</div>
    <h2 class="section-title">Four places. One job each.</h2>
    <p class="section-sub">Browse is the global pool. My recipes is your library. This Week is the shape, then the shop. Profile is diet, taste, usual week, and support.</p>
    <div class="doc-grid">
      <a class="doc-card" href="prototype.html"><b>Prototype</b><span>Interactive freeze. Use “load populated demo” for the full click-through.</span></a>
      <a class="doc-card" href="prd.html"><b>PRD</b><span>Requirements, users, metrics.</span></a>
      <a class="doc-card" href="design.html"><b>Design v1.6</b><span>Screens and flows. Review: approved with changes.</span></a>
      <a class="doc-card" href="architecture.html"><b>Architecture v1.1</b><span>Browse load, fillWeek, extract tools. Review: needs rework.</span></a>
      <a class="doc-card" href="sketch.html"><b>Solution sketch</b><span>Entities and contracts through delta #15.</span></a>
      <a class="doc-card" href="decisions.html"><b>Decisions</b><span>Logged product and stack calls.</span></a>
    </div>
  </div>
</section>
</body>
</html>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    proto = VAULT / "Prototype-v2.html"
    (OUT / "prototype.html").write_text(proto.read_text(encoding="utf-8"), encoding="utf-8")
    assets_dst = OUT / "prototype-assets"
    assets_dst.mkdir(exist_ok=True)
    for img in (VAULT / "prototype-assets").glob("*.jpg"):
        (assets_dst / img.name).write_bytes(img.read_bytes())

    (OUT / "index.html").write_text(INDEX, encoding="utf-8")

    for html_name, md_name, title, meta, src_name in DOC_PAGES:
        src = VAULT / src_name
        body, toc = convert(src)
        (OUT / html_name).write_text(wrap_doc(title, meta, body, toc), encoding="utf-8")
        if md_name:
            (OUT / md_name).write_text(md_for_repo(src.read_text(encoding="utf-8")), encoding="utf-8")
        print("wrote", html_name, "+" if md_name else "", md_name or "")


if __name__ == "__main__":
    main()
