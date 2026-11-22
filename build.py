#!/usr/bin/env python3
"""Build the Signal & Shield static blog from posts/*.json into docs/.

Standard library only. Run: python3 build.py
Validates every post; exits non-zero on any schema error so a bad post never ships.
"""
import json, re, sys, shutil
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
POSTS = ROOT / "posts"
OUT = ROOT / "docs"
SITE_TITLE = "Signal & Shield"
SITE_TAGLINE = "A daily briefing on cybersecurity and AI, by Simon Boadi"
SITE_URL = "https://l1ght41.github.io/cyber-ai-briefing"
PORTFOLIO_URL = "https://simon-boadi-cybersecurity.pplx.app"
SECTION_KEYS = {"cyber": "Cybersecurity", "ai": "AI & Tech"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(msg):
    print(f"BUILD ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def validate(p, path):
    for k in ("date", "title", "summary", "sections", "takeaway"):
        if not p.get(k):
            fail(f"{path.name}: missing '{k}'")
    if not DATE_RE.match(p["date"]) or path.stem != p["date"]:
        fail(f"{path.name}: date must be YYYY-MM-DD and match the filename")
    keys = [s.get("key") for s in p["sections"]]
    if sorted(keys) != ["ai", "cyber"]:
        fail(f"{path.name}: sections must be exactly 'cyber' and 'ai'")
    for s in p["sections"]:
        items = s.get("items") or []
        if not 2 <= len(items) <= 7:
            fail(f"{path.name}: section {s['key']} needs 2-7 items")
        for i, it in enumerate(items):
            for k in ("headline", "body", "why", "sources"):
                if not it.get(k):
                    fail(f"{path.name}: {s['key']} item {i+1} missing '{k}'")
            for src in it["sources"]:
                if not src.get("name") or not str(src.get("url", "")).startswith(("http://", "https://")):
                    fail(f"{path.name}: {s['key']} item {i+1} has a bad source")


def load_posts():
    posts = []
    for path in sorted(POSTS.glob("*.json")):
        try:
            p = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{path.name}: invalid JSON ({e})")
        validate(p, path)
        posts.append(p)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def nice_date(d):
    dt = date.fromisoformat(d)
    return dt.strftime("%A, %B ") + str(dt.day) + dt.strftime(", %Y")


def page(title, desc, body, rel="", canonical=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{escape(canonical or SITE_URL + '/')}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:type" content="article">
<link rel="alternate" type="application/rss+xml" title="{SITE_TITLE}" href="{rel}feed.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%2316181d'/%3E%3Cpath d='M16 6l8 3v6c0 5-3.4 8.8-8 11-4.6-2.2-8-6-8-11V9z' fill='none' stroke='%23e8590c' stroke-width='2.4'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://api.fontshare.com">
<link href="https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@500,700,800&f[]=satoshi@400,500,700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap masthead-row">
    <a class="brand" href="{rel}index.html" aria-label="{SITE_TITLE} home">
      <svg viewBox="0 0 32 32" width="26" height="26" aria-hidden="true"><path d="M16 4l10 3.6v7.2c0 6-4.2 10.6-10 13.2C10.2 25.4 6 20.8 6 14.8V7.6z" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M11 16h3l2-4 2 8 2-4h1" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <span>{SITE_TITLE}</span>
    </a>
    <nav aria-label="Primary">
      <a href="{rel}index.html">Briefings</a>
      <a href="{rel}archive.html">Archive</a>
      <a href="{rel}about.html">About</a>
      <a class="nav-cta" href="{PORTFOLIO_URL}">Portfolio</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-row">
    <p>{SITE_TITLE} &middot; {escape(SITE_TAGLINE)}.</p>
    <p><a href="{PORTFOLIO_URL}">Portfolio</a> &middot; <a href="{rel}feed.xml">RSS</a> &middot; Summaries link to original reporting; read the sources for full detail.</p>
  </div>
</footer>
</body>
</html>
"""


def render_sources(srcs):
    links = ", ".join(
        f'<a href="{escape(s["url"])}" rel="noopener" target="_blank">{escape(s["name"])}</a>' for s in srcs)
    return f'<p class="sources"><span>Sources</span> {links}</p>'


def render_post_body(p):
    out = []
    for s in sorted(p["sections"], key=lambda s: 0 if s["key"] == "cyber" else 1):
        label = SECTION_KEYS[s["key"]]
        items = []
        for n, it in enumerate(s["items"], 1):
            items.append(f"""<article class="item">
  <div class="item-num">{n:02d}</div>
  <div class="item-body">
    <h3>{escape(it["headline"])}</h3>
    <p>{escape(it["body"])}</p>
    <p class="why"><strong>Why it matters</strong> {escape(it["why"])}</p>
    {render_sources(it["sources"])}
  </div>
</article>""")
        out.append(f"""<section class="desk desk-{s['key']}" aria-labelledby="h-{s['key']}">
  <h2 id="h-{s['key']}"><span class="tag tag-{s['key']}">{label}</span><span class="count">{len(s['items'])} stories</span></h2>
  {''.join(items)}
</section>""")
    return "\n".join(out)


def post_html(p, prev_p, next_p):
    nav = []
    if next_p:
        nav.append(f'<a href="{next_p["date"]}.html">&larr; Newer: {escape(nice_date(next_p["date"]))}</a>')
    if prev_p:
        nav.append(f'<a class="older" href="{prev_p["date"]}.html">Older: {escape(nice_date(prev_p["date"]))} &rarr;</a>')
    body = f"""<div class="wrap narrow">
<p class="kicker">Daily briefing &middot; <time datetime="{p['date']}">{nice_date(p['date'])}</time></p>
<h1 class="post-title">{escape(p['title'])}</h1>
<p class="lede">{escape(p['summary'])}</p>
{render_post_body(p)}
<aside class="takeaway"><h2>The takeaway</h2><p>{escape(p['takeaway'])}</p></aside>
<nav class="post-nav" aria-label="Briefing navigation">{''.join(nav)}</nav>
</div>"""
    return page(f"{p['title']} | {SITE_TITLE}", p["summary"], body, rel="../",
                canonical=f"{SITE_URL}/posts/{p['date']}.html")


def card(p, rel=""):
    heads = [it["headline"] for s in sorted(p["sections"], key=lambda s: s["key"] != "cyber") for it in s["items"][:2]]
    li = "".join(f"<li>{escape(h)}</li>" for h in heads)
    return f"""<article class="card">
  <p class="kicker"><time datetime="{p['date']}">{nice_date(p['date'])}</time></p>
  <h3><a href="{rel}posts/{p['date']}.html">{escape(p['title'])}</a></h3>
  <ul>{li}</ul>
</article>"""


def index_html(posts):
    if not posts:
        body = '<div class="wrap"><p class="empty">The first briefing is on its way.</p></div>'
        return page(SITE_TITLE, SITE_TAGLINE, body)
    latest, rest = posts[0], posts[1:8]
    recent = "".join(card(p) for p in rest) or '<p class="empty">Earlier briefings will appear here.</p>'
    body = f"""<section class="hero">
  <div class="wrap">
    <p class="kicker">Today's briefing &middot; <time datetime="{latest['date']}">{nice_date(latest['date'])}</time></p>
    <h1><a href="posts/{latest['date']}.html">{escape(latest['title'])}</a></h1>
    <p class="lede">{escape(latest['summary'])}</p>
    <p><a class="btn" href="posts/{latest['date']}.html">Read today's briefing</a></p>
  </div>
</section>
<div class="wrap narrow">
{render_post_body(latest)}
<aside class="takeaway"><h2>The takeaway</h2><p>{escape(latest['takeaway'])}</p></aside>
</div>
<section class="recent"><div class="wrap"><h2 class="section-title">Recent briefings</h2><div class="grid">{recent}</div>
<p><a href="archive.html">Full archive &rarr;</a></p></div></section>"""
    return page(f"{SITE_TITLE} | Daily cybersecurity & AI briefing", latest["summary"], body)


def archive_html(posts):
    rows = "".join(
        f'<li><time datetime="{p["date"]}">{p["date"]}</time><a href="posts/{p["date"]}.html">{escape(p["title"])}</a></li>'
        for p in posts) or '<li>No briefings yet.</li>'
    body = f'<div class="wrap narrow"><h1 class="post-title">Archive</h1><p class="lede">Every daily briefing, newest first.</p><ol class="archive">{rows}</ol></div>'
    return page(f"Archive | {SITE_TITLE}", "All Signal & Shield briefings.", body, canonical=f"{SITE_URL}/archive.html")


def about_html():
    body = f"""<div class="wrap narrow prose">
<h1 class="post-title">About {SITE_TITLE}</h1>
<p class="lede">A short, sourced morning read on what changed in cybersecurity and AI, and why it matters to the people who defend systems.</p>
<p>{SITE_TITLE} is published every morning by Simon Boadi, a cybersecurity engineer working across cloud security, DevSecOps and AI governance. Each briefing covers the most significant security stories (breaches, actively exploited vulnerabilities, threat activity and policy) alongside the AI developments that shape how software is built and secured.</p>
<p>Every item links to its original reporting. Summaries are written for practitioners: what happened, and why it matters.</p>
<p>Briefings are researched and drafted with AI assistance from public reporting and published automatically, so always check the linked sources before acting on anything here.</p>
<p><a class="btn" href="{PORTFOLIO_URL}">View Simon's portfolio</a></p>
</div>"""
    return page(f"About | {SITE_TITLE}", SITE_TAGLINE, body, canonical=f"{SITE_URL}/about.html")


def feed_xml(posts):
    items = []
    for p in posts[:30]:
        dt = datetime.fromisoformat(p["date"] + "T13:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
        items.append(f"""<item><title>{escape(p['title'])}</title><link>{SITE_URL}/posts/{p['date']}.html</link>
<guid>{SITE_URL}/posts/{p['date']}.html</guid><pubDate>{dt}</pubDate><description>{escape(p['summary'])}</description></item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{SITE_TITLE}</title><link>{SITE_URL}/</link>
<description>{escape(SITE_TAGLINE)}</description>{''.join(items)}</channel></rss>
"""


def main():
    posts = load_posts()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "posts").mkdir(parents=True)
    shutil.copy(ROOT / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(index_html(posts), encoding="utf-8")
    (OUT / "archive.html").write_text(archive_html(posts), encoding="utf-8")
    (OUT / "about.html").write_text(about_html(), encoding="utf-8")
    (OUT / "feed.xml").write_text(feed_xml(posts), encoding="utf-8")
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        (OUT / "posts" / f"{p['date']}.html").write_text(post_html(p, older, newer), encoding="utf-8")
    print(f"Built {len(posts)} post(s) into docs/")


if __name__ == "__main__":
    main()
