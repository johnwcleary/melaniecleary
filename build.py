#!/usr/bin/env python3
"""Builds the static site in ./site from content.json.

Usage: python3 build.py
Everything under site/assets is hand-written and left alone; the HTML pages are regenerated.
"""
import html
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site"
DATA = json.loads((ROOT / "content.json").read_text())
SITE = DATA["site"]
PROJECTS = DATA["projects"]
# Root URL path the site is served from ("/" on a custom domain, "/repo/" on github.io).
BASE = os.environ.get("BASE_PATH", "").rstrip("/") + "/"
FONTS = "https://fonts.googleapis.com/css2?family=Chivo:wght@400;700;900&family=Nunito:ital,wght@0,400;0,600;0,700;1,400&display=swap"

esc = html.escape


def page(title, body, *, depth, active, description=None, image=None, body_class="", base=None):
    up = base if base is not None else "../" * depth
    full_title = f"{title} — {SITE['name']}" if title else f"{SITE['name']} — {SITE['tagline']}"
    desc = esc(description or SITE["description"])
    og_image = f'<meta property="og:image" content="{SITE["url"]}/assets/img/{image}">' if image else ""
    current = ' aria-current="page"'

    def nav(key, href, label):
        return f'<a href="{up}{href}"{current if active == key else ""}>{label}</a>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
{og_image}
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{up}assets/css/style.css">
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header wrap">
  <a class="brand" href="{up}">
    <span class="brand-name">{esc(SITE['name'])}</span>
    <span class="brand-tag">{esc(SITE['tagline'])}</span>
  </a>
  <nav class="site-nav" aria-label="Main">
    {nav("work", "", "Work")}
    {nav("about", "about/", "About")}
  </nav>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer wrap">
  <span>© {date.today().year} {esc(SITE['name'])}</span>
  <a href="#main" class="to-top">Back to top ↑</a>
</footer>
<script src="{up}assets/js/main.js" defer></script>
</body>
</html>
"""


def video(b):
    src = f"https://player.vimeo.com/video/{b['id']}?"
    if b.get("h"):
        src += f"h={b['h']}&"
    src += "title=0&byline=0&portrait=0&dnt=1"
    w, h = b["ratio"].split("/")
    tall = " is-tall" if int(h) > int(w) else ""
    return (
        f'<figure class="media video{tall}" style="aspect-ratio:{b["ratio"]}">'
        f'<iframe src="{src}" title="{esc(b["title"])}" loading="lazy" '
        f'allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></figure>'
    )


def image(src, alt, up, cls="media image"):
    return f'<figure class="{cls}"><img src="{up}assets/img/{src}" alt="{esc(alt)}" loading="lazy" decoding="async"></figure>'


def block(b, up):
    t = b["type"]
    if t == "text":
        return '<div class="prose">' + "".join(f"<p>{p}</p>" for p in b["html"]) + "</div>"
    if t == "video":
        return video(b)
    if t == "image":
        return image(b["src"], b["alt"], up)
    if t == "row":
        cols = b.get("cols", len(b["items"]))
        align = " row-center" if b.get("align") == "center" else ""
        inner = "".join(block(i, up) for i in b["items"])
        return f'<div class="row{align}" style="--cols:{cols}">{inner}</div>'
    if t == "gallery":
        items = "".join(
            f'<a class="gallery-item" href="{up}assets/img/{i["src"]}" data-lightbox>'
            f'<img src="{up}assets/img/{i["src"]}" alt="{esc(i["alt"])}" loading="lazy" decoding="async"></a>'
            for i in b["items"]
        )
        return f'<div class="gallery">{items}</div>'
    if t in ("credits", "awards"):
        label = "Credits" if t == "credits" else "Recognition"
        rows = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in b["items"])
        return f'<section class="meta-list {t}" aria-label="{label}"><h2>{label}</h2><dl>{rows}</dl></section>'
    raise ValueError(f"unknown block type {t!r}")


def work_grid():
    cards = []
    for i, p in enumerate(PROJECTS):
        loading = "eager" if i < 3 else "lazy"
        cards.append(
            f'<li><a class="card" href="{p["slug"]}/">'
            f'<img src="assets/img/{p["thumb"]}" alt="" loading="{loading}" decoding="async">'
            f'<span class="card-title">{esc(p["title"])}</span></a></li>'
        )
    body = f'<h1 class="visually-hidden">Selected work</h1><ul class="work-grid wrap">{"".join(cards)}</ul>'
    return page(None, body, depth=0, active="work", image=PROJECTS[0]["thumb"], body_class="home")


def project_page(i, p):
    up = "../"
    prev_p = PROJECTS[i - 1]
    next_p = PROJECTS[(i + 1) % len(PROJECTS)]
    kicker = f'<p class="kicker">{esc(p["kicker"])}</p>' if p.get("kicker") else ""
    sub = f'<p class="subtitle">{esc(p["subtitle"])}</p>' if p.get("subtitle") else ""
    blocks = "\n".join(block(b, up) for b in p["blocks"])
    first_text = next((b["html"][0] for b in p["blocks"] if b["type"] == "text"), None)
    desc = html.unescape(first_text.replace("<em>", "").replace("</em>", "")) if first_text else None
    body = f"""<article class="project wrap">
  <header class="project-head">{kicker}<h1>{esc(p['title'])}</h1>{sub}</header>
  <div class="project-body">
{blocks}
  </div>
</article>
<nav class="pager wrap" aria-label="More work">
  <a class="pager-link prev" href="{up}{prev_p['slug']}/"><span>Previous</span><strong>{esc(prev_p['title'])}</strong></a>
  <a class="pager-all" href="{up}">All work</a>
  <a class="pager-link next" href="{up}{next_p['slug']}/"><span>Next</span><strong>{esc(next_p['title'])}</strong></a>
</nav>"""
    title = p["title"] + (f": {p['subtitle']}" if p.get("subtitle") and not p["subtitle"].startswith("+") else "")
    return page(title, body, depth=1, active="work", description=desc, image=p["thumb"])


def about_page():
    a = DATA["about"]
    paras = "".join(f"<p>{esc(t)}</p>" for t in a["body"])
    facts = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in a["facts"])
    body = f"""<section class="about wrap">
  <div class="about-text">
    <h1 class="visually-hidden">About</h1>
    <div class="prose lead">{paras}</div>
    <dl class="facts">{facts}</dl>
  </div>
  {image(a['photo'], 'Melanie Cleary', '../', 'about-photo')}
</section>"""
    return page("About", body, depth=1, active="about", image=a["photo"])


def not_found():
    body = f'<section class="wrap notfound"><h1>Page not found</h1><p class="prose">That page doesn’t exist. <a href="{BASE}">See all work →</a></p></section>'
    # Served at arbitrary missing URLs, so asset paths must be root-relative.
    return page("Not found", body, depth=0, active=None, base=BASE)


def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print("wrote", path.relative_to(ROOT))


write("index.html", work_grid())
write("about/index.html", about_page())
write("404.html", not_found())
for i, p in enumerate(PROJECTS):
    write(f"{p['slug']}/index.html", project_page(i, p))
