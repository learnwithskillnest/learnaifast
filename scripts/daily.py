#!/usr/bin/env python3
"""Publish one LearnAIFast daily AI update.

Usage:  python3 scripts/daily.py daily/_data/2026-11-03.json

The JSON file holds one day's post:
{
  "date": "2026-11-03",                       # YYYY-MM-DD (IST date)
  "title": "...",                             # 50-70 chars, keyword first
  "summary": "...",                           # meta description, 120-160 chars
  "intro": "...",                             # 1-2 sentences
  "news": [                                   # 3-5 items, written in our own words
    {"headline": "...", "body": "...", "why": "...",
     "source_name": "...", "source_url": "https://..."}
  ],
  "tip":   {"title": "...", "body": "...", "prompt": "..."},   # prompt of the day
  "tags":  ["ChatGPT", "Gemini", ...]
}

What it does (idempotent, re-running the same day overwrites that day):
  * writes /daily/<date>-<slug>/index.html (the permanent post page)
  * keeps an index of every post in daily/posts.json
  * rebuilds /daily/index.html (latest post on top, archive below)
  * replaces the homepage block between <!-- DAILY:START --> and <!-- DAILY:END -->
  * rebuilds /daily/feed.xml (RSS) and the daily section of sitemap.xml
"""
import datetime as dt
import html
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://learnaifast.in"
DAILY = ROOT / "daily"
INDEX = DAILY / "posts.json"

e = lambda s: html.escape(str(s or ""), quote=True)


def slugify(s, n=55):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    if len(s) > n:
        s = s[:n].rsplit("-", 1)[0]
    return s.strip("-") or "ai-update"


def seo_title(t, limit=62):
    """Search-result title: full headline + brand if it fits, else the leading clauses."""
    t = t.strip()
    for c in (f"{t} | LearnAIFast", t):
        if len(c) <= limit:
            return c
    parts = re.split(r"(?i),\s+|\s+and\s+(?=more\b)", t)
    out = parts[0]
    for x in parts[1:]:
        if len(out) + 2 + len(x) > limit or x.lower() == "more":
            break
        out += ", " + x
    if len(out) > limit:
        out = out[:limit - 1].rsplit(" ", 1)[0] + "…"
    return out if len(out) + 14 > limit else out + " | LearnAIFast"


def nice(d):
    d = dt.date.fromisoformat(d)
    return f"{d.day} {d.strftime('%B %Y')}"


def head(title, desc, url, ld, ogtype="article", extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="LearnAIFast">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="LearnAIFast: practical AI guides and free tools for India">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="LearnAIFast Daily AI Update" href="/daily/feed.xml">
<meta name="theme-color" content="#0E7A6A">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/site.css">{extra}
<script type="application/ld+json">
{json.dumps(ld, indent=1, ensure_ascii=False)}
</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9472711790336039" crossorigin="anonymous"></script>
</head>
<body>
"""


def shell_parts():
    """Reuse the live header and footer from the guides page so the nav stays in sync."""
    g = (ROOT / "guides" / "index.html").read_text(encoding="utf-8")
    header = re.search(r'<header class="top">.*?</header>', g, re.S).group(0)
    header = header.replace(' aria-current="page"', "")
    header = header.replace('<a href="/daily/">Daily</a>', '<a href="/daily/" aria-current="page">Daily</a>')
    footer = re.search(r"<footer>.*?</footer>", g, re.S).group(0)
    return header, footer


ORG = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "LearnAIFast",
       "url": f"{SITE}/", "logo": f"{SITE}/icon-512.png", "email": "learnwithskillnest@gmail.com"}


def post_url(p):
    return f"{SITE}/daily/{p['date']}-{p['slug']}/"


def build_post(p, prev, nxt, header, footer):
    url = post_url(p)
    ld = {"@context": "https://schema.org", "@graph": [ORG, {
        "@type": "NewsArticle", "headline": p["title"][:110], "description": p["summary"],
        "url": url, "mainEntityOfPage": url, "image": f"{SITE}/og-image.png",
        "datePublished": f"{p['date']}T08:00:00+05:30", "dateModified": f"{p['date']}T08:00:00+05:30",
        "inLanguage": "en-IN", "keywords": ", ".join(p.get("tags", [])),
        "author": {"@id": f"{SITE}/#org"}, "publisher": {"@id": f"{SITE}/#org"}}, {
        "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Daily AI Update", "item": f"{SITE}/daily/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]}
    news = "\n".join(f"""  <h2>{i}. {e(n['headline'])}</h2>
  <p>{e(n['body'])}</p>
  <p><b>Why it matters for you:</b> {e(n['why'])}</p>
  <p class="src">Source: <a href="{e(n['source_url'])}" rel="noopener" target="_blank">{e(n['source_name'])}</a></p>"""
                     for i, n in enumerate(p["news"], 1))
    t = p["tip"]
    nav = []
    if prev:
        nav.append(f'← <a href="/daily/{prev["date"]}-{prev["slug"]}/">{e(prev["title"])}</a>')
    if nxt:
        nav.append(f'<a href="/daily/{nxt["date"]}-{nxt["slug"]}/">{e(nxt["title"])}</a> →')
    tags = " ".join(f'<span class="dtag">#{e(x)}</span>' for x in p.get("tags", []))
    body = f"""{header}

<main class="wrap">
<article class="page read">
  <div class="crumbs"><a href="/">Home</a> / <a href="/daily/">Daily AI Update</a> / <span>{e(nice(p['date']))}</span></div>
  <div class="eyebrow">Daily AI Update · {e(nice(p['date']))}</div>
  <h1>{e(p['title'])}</h1>
  <div class="art-meta">{max(2, len(p['news']) + 1)} min read · <time datetime="{p['date']}">{e(nice(p['date']))}</time></div>
  <p class="lede">{e(p['intro'])}</p>

{news}

  <h2>Prompt of the day: {e(t['title'])}</h2>
  <p>{e(t['body'])}</p>
  <div class="prompt"><span class="pl">Copy &amp; try</span><span class="t">{e(t['prompt'])}</span></div>

  <p class="dtags">{tags}</p>
  <div class="note">New AI update every morning. Bookmark <a href="/daily/">learnaifast.in/daily</a> or follow the <a href="/daily/feed.xml">RSS feed</a>.</div>
  <p class="next">{' · '.join(nav) or '<a href="/daily/">All daily updates</a>'}<br>Learn the basics: <a href="/what-is-ai/">What Is AI?</a> · <a href="/how-to-write-ai-prompts/">How to Write Better AI Prompts</a></p>
</article>
</main>

{footer}
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    out = DAILY / f"{p['date']}-{p['slug']}" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head(seo_title(p['title']), p["summary"], url, ld) + body, encoding="utf-8")


def card(p):
    return (f'<a class="card" href="/daily/{p["date"]}-{p["slug"]}/"><span class="tag">{e(nice(p["date"]))}</span>'
            f'<h3>{e(p["title"])}</h3><p>{e(p["summary"])}</p><span class="meta">Daily AI Update</span></a>')


def build_hub(posts, header, footer):
    url = f"{SITE}/daily/"
    latest = posts[0]
    desc = ("Today's AI news in simple words for India: what's new in ChatGPT, Gemini and Claude, why it matters, "
            "and a free prompt of the day.")
    ld = {"@context": "https://schema.org", "@graph": [ORG, {
        "@type": "CollectionPage", "name": "Daily AI Update", "url": url, "description": desc,
        "inLanguage": "en-IN", "dateModified": latest["date"], "publisher": {"@id": f"{SITE}/#org"},
        "mainEntity": {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i, "url": post_url(p), "name": p["title"]}
            for i, p in enumerate(posts[:30], 1)]}}]}
    heads = "".join(f"<li>{e(n['headline'])}</li>" for n in latest["news"])
    body = f"""{header}

<main class="wrap">
<section class="page">
  <div class="eyebrow">Updated every morning</div>
  <h1>Daily AI Update: <mark class="hl">today's AI news in simple words</mark></h1>
  <p class="lede">Every day we pick the AI news that actually matters to students, job seekers and small businesses in India, explain it plainly, and add one prompt you can try right away.</p>

  <div class="today">
    <div class="today-top"><span class="live">Today</span><time datetime="{latest['date']}">{e(nice(latest['date']))}</time></div>
    <h2><a href="/daily/{latest['date']}-{latest['slug']}/">{e(latest['title'])}</a></h2>
    <p>{e(latest['summary'])}</p>
    <ul>{heads}</ul>
    <a class="btn primary" href="/daily/{latest['date']}-{latest['slug']}/">Read today's update</a>
  </div>

  <h2>Earlier updates</h2>
  <div class="cards">
    {chr(10).join('    ' + card(p) for p in posts[1:60]) or '<p>More updates coming tomorrow.</p>'}
  </div>
  <p class="note">Want these in a feed reader? Use <a href="/daily/feed.xml">learnaifast.in/daily/feed.xml</a>.</p>
</section>
</main>

{footer}
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    (DAILY / "index.html").write_text(
        head("Daily AI Update: Today's AI News in Simple Words (India)", desc, url, ld, "website") + body,
        encoding="utf-8")


def build_home_block(p):
    heads = "".join(f"<li>{e(n['headline'])}</li>" for n in p["news"][:3])
    block = f"""<!-- DAILY:START (auto-generated by scripts/daily.py, do not edit by hand) -->
  <div class="today">
    <div class="today-top"><span class="live">Today's AI update</span><time datetime="{p['date']}">{e(nice(p['date']))}</time></div>
    <h2><a href="/daily/{p['date']}-{p['slug']}/">{e(p['title'])}</a></h2>
    <ul>{heads}</ul>
    <div class="btns"><a class="btn primary" href="/daily/{p['date']}-{p['slug']}/">Read today's update</a><a class="btn ghost" href="/daily/">All daily updates</a></div>
  </div>
  <!-- DAILY:END -->"""
    f = ROOT / "index.html"
    s = f.read_text(encoding="utf-8")
    if "<!-- DAILY:START" in s:
        s = re.sub(r"<!-- DAILY:START.*?<!-- DAILY:END -->", lambda m: block, s, flags=re.S)
    else:  # first run: put it at the very top of the page, above the hero
        s = s.replace('<section class="page">\n  <div class="hero">',
                      '<section class="page">\n  ' + block + '\n  <div class="hero">', 1)
    if 'type="application/rss+xml"' not in s:
        s = s.replace('<link rel="stylesheet" href="/assets/site.css">',
                      '<link rel="stylesheet" href="/assets/site.css">\n<link rel="alternate" type="application/rss+xml" '
                      'title="LearnAIFast Daily AI Update" href="/daily/feed.xml">', 1)
    f.write_text(s, encoding="utf-8")


def build_feed(posts):
    items = []
    for p in posts[:30]:
        d = dt.datetime.fromisoformat(f"{p['date']}T08:00:00+05:30")
        items.append(f"""  <item>
    <title>{e(p['title'])}</title>
    <link>{post_url(p)}</link>
    <guid isPermaLink="true">{post_url(p)}</guid>
    <pubDate>{d.strftime('%a, %d %b %Y %H:%M:%S +0530')}</pubDate>
    <description>{e(p['summary'])}</description>
  </item>""")
    (DAILY / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>LearnAIFast Daily AI Update</title>
  <link>{SITE}/daily/</link>
  <atom:link href="{SITE}/daily/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Today's AI news in simple words for India, plus a prompt of the day.</description>
  <language>en-in</language>
{chr(10).join(items)}
</channel>
</rss>
""", encoding="utf-8")


def update_sitemap(posts):
    f = ROOT / "sitemap.xml"
    s = f.read_text(encoding="utf-8")
    s = re.sub(r"\s*<url><loc>https://learnaifast\.in/daily/[^<]*</loc>.*?</url>", "", s)
    today = posts[0]["date"]
    s = re.sub(r"(<url><loc>https://learnaifast\.in/</loc><lastmod>)[^<]*", r"\g<1>" + today, s)
    rows = [f'  <url><loc>{SITE}/daily/</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>']
    rows += [f'  <url><loc>{post_url(p)}</loc><lastmod>{p["date"]}</lastmod><priority>0.7</priority></url>' for p in posts]
    s = re.sub(r"(<url><loc>https://learnaifast\.in/</loc>.*?</url>)", lambda m: m.group(1) + "\n" + "\n".join(rows), s, count=1)
    f.write_text(s, encoding="utf-8")


def main():
    src = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    dt.date.fromisoformat(src["date"])
    for k in ("title", "summary", "intro", "news", "tip"):
        assert src.get(k), f"missing {k}"
    assert 2 <= len(src["news"]) <= 6, "need 2-6 news items"
    for n in src["news"]:
        assert n["source_url"].startswith("http"), "every news item needs a source link"
    src["slug"] = src.get("slug") or slugify(src["title"])

    posts = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else []
    for old in [p for p in posts if p["date"] == src["date"] and p["slug"] != src["slug"]]:
        shutil.rmtree(DAILY / f"{old['date']}-{old['slug']}", ignore_errors=True)
    posts = [p for p in posts if p["date"] != src["date"]]
    posts.append(src)
    posts.sort(key=lambda p: p["date"], reverse=True)
    INDEX.write_text(json.dumps(posts, indent=1, ensure_ascii=False), encoding="utf-8")

    header, footer = shell_parts()
    for i, p in enumerate(posts):  # rebuild neighbours so prev/next links stay correct
        if i <= 1 or p["date"] == src["date"]:
            build_post(p, posts[i + 1] if i + 1 < len(posts) else None, posts[i - 1] if i else None, header, footer)
    build_hub(posts, header, footer)
    build_home_block(posts[0])
    build_feed(posts)
    update_sitemap(posts)
    print("published", post_url(src))


if __name__ == "__main__":
    main()
