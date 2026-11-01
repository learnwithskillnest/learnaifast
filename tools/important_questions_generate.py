#!/usr/bin/env python3
"""Generate /important-questions/ pages for learnaifast.in from groups.json.
Usage: python3 gen.py /home/claude/learnaifast groups.json
"""
import html, json, os, re, sys

ROOT, DATA = sys.argv[1], sys.argv[2]
SITE, TODAY = "https://learnaifast.in", "2026-11-01"
G = json.load(open(DATA, encoding="utf-8"))
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "LearnAIFast", "url": SITE + "/", "logo": SITE + "/icon-512.png", "email": "learnwithskillnest@gmail.com"}
E = html.escape
tpl = open(os.path.join(ROOT, "what-is-ai/index.html"), encoding="utf-8").read()

CSS = """<style>
/* Important-questions pages: ranked list of repeated questions with years and variants, then unit-wise recent questions. */
.iq-how{background:var(--soft);border-radius:10px;padding:12px 16px;font-size:15.5px;margin:18px 0}
.iq-list{list-style:none;padding:0;margin:14px 0 0;counter-reset:iq;display:grid;gap:12px}
.iq-list>li{counter-increment:iq;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px 12px 52px;position:relative;max-width:none}
.iq-list>li::before{content:counter(iq);position:absolute;left:14px;top:14px;width:26px;height:26px;border-radius:50%;background:var(--accent);color:var(--accent-ink);font:700 13px/26px var(--display);text-align:center}
.iq-q{font-weight:600;line-height:1.5}
.iq-meta{font-family:var(--mono);font-size:12.5px;color:var(--muted);margin-top:6px;line-height:1.7}
.iq-meta a{color:var(--muted)}
.iq-badge{display:inline-block;background:var(--mark);color:#14211D;border-radius:4px;padding:0 6px;font-weight:600;margin-right:6px}
.iq-var{margin:6px 0 0;padding-left:18px;font-size:14.5px;color:var(--muted)}
.iq-var li{margin:2px 0}
details.iq-unit{border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:10px 0;background:var(--surface)}
details.iq-unit summary{font:700 17px var(--display);cursor:pointer}
details.iq-unit ul{margin:10px 0 4px;padding-left:20px}
details.iq-unit li{margin:6px 0}
details.iq-unit small{font-family:var(--mono);font-size:12px;color:var(--muted)}
.iq-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:16px}
.iq-card{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.iq-card:hover{border-color:var(--accent)}
.iq-card b{display:block;font-family:var(--display);font-size:17px}
.iq-card span{font-family:var(--mono);font-size:12.5px;color:var(--muted)}
</style>"""

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}

def ld(graph):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)

def sub1(pat, rep, s, flags=0):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags); assert n == 1, pat; return out

def build(path, title, desc, body, graph):
    url = SITE + path; e = lambda x: E(x, quote=True); s = tpl
    s = sub1(r"<title>.*?</title>", "<title>%s</title>" % E(title), s)
    s = sub1(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % e(desc), s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % url, s)
    s = sub1(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="website">', s)
    for a, n, v in [("property", "og:title", title), ("name", "twitter:title", title), ("property", "og:description", desc), ("name", "twitter:description", desc), ("property", "og:url", url)]:
        s = sub1(r'<meta %s="%s" content="[^"]*">' % (a, n), '<meta %s="%s" content="%s">' % (a, n, e(v)), s)
    s = sub1(r'<script type="application/ld\+json">.*?</script>', ld(graph), s, re.S)
    s = s.replace("</head>", CSS + "\n</head>", 1)
    s = sub1(r'<main class="wrap">\n.*?\n</main>', '<main class="wrap">\n%s\n</main>' % body, s, re.S)
    s = s.replace('<a href="/guides/" aria-current="page">Guides</a>', '<a href="/guides/">Guides</a>')
    s = s.replace('<a href="/papers/">Papers</a>', '<a href="/papers/" aria-current="page">Papers</a>', 1)
    d = os.path.join(ROOT, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(s)

def years_links(papers):
    return " · ".join('<a href="/papers/%s">%s %s</a>' % (pg, E(sess), E(code)) for sess, code, pg in papers)

def row(r):
    meta = '<span class="iq-badge">Asked in %d papers</span>' % r["times"]
    if r.get("unit"): meta += "Unit %d · " % r["unit"]
    meta += years_links(r["papers"])
    var = ""
    if r["variants"]:
        var = '<div class="iq-meta" style="margin-top:8px">Also asked as:</div><ul class="iq-var">%s</ul>' % "".join("<li>%s</li>" % E(v) for v in r["variants"])
    return '    <li><div class="iq-q">%s</div><div class="iq-meta">%s</div>%s</li>' % (E(r["q"]), meta, var)

def page_for(g):
    n = len(g["papers"]); oldest, latest = g["papers"][-1]["session"], g["papers"][0]["session"]
    course = g["course"]; name = g["name"]; plain = name.replace("MCA ", "")
    head = "AKTU %s Important Questions" % name
    title = head + (" (PYQ-Based)" if len(head) < 48 else "")
    desc = ("Most repeated AKTU %s %s questions from %d previous year papers (%s to %s), with years asked and unit-wise questions." % (course, plain, n, oldest, latest))
    if len(desc) > 158: desc = "Most repeated AKTU %s questions from %d previous year papers (%s to %s), with years asked and unit-wise lists." % (plain, n, oldest, latest)
    long_rows, short_rows = g["long"][:25], g["short"][:20]
    b = []
    b.append('  <div class="crumbs"><a href="/">Home</a> / <a href="/papers/">Papers</a> / <a href="/important-questions/">Important questions</a> / <span>%s</span></div>' % E(name))
    b.append('  <div class="eyebrow">AKTU · %s · Important questions</div>' % E(course))
    b.append("  <h1>%s</h1>" % E(head))
    b.append('  <p class="lede">The questions AKTU asks again and again in %s, found by comparing every question in %d previous year papers from %s to %s (subject codes %s).</p>' % (E(plain), n, E(oldest), E(latest), E(", ".join(g["codes"]))))
    b.append('  <div class="iq-how"><strong>How this list is made:</strong> we compared all %d questions in these papers and grouped the ones that ask about the same thing. Each item shows how many papers it appeared in, which years, and other ways it was worded. Topics that come back often are a strong hint, not a guarantee, so study your full syllabus too.</div>' % g["nquestions"])
    if long_rows:
        b.append("  <h2>Most repeated long questions</h2>")
        b.append('  <p>From Sections B and C (7 or 10 marks, depending on the year). Unit numbers come from Section C, where each question covers one unit.</p>')
        b.append('  <ol class="iq-list">\n%s\n  </ol>' % "\n".join(row(r) for r in long_rows))
    if short_rows:
        b.append("  <h2>Most repeated short questions (2 marks)</h2>")
        b.append('  <p>From Section A. Learn a crisp definition plus one example or line of explanation for each.</p>')
        b.append('  <ol class="iq-list">\n%s\n  </ol>' % "\n".join(row(r) for r in short_rows))
    if g["units"]:
        recent = sorted({(x["session"], x["code"]) for us in g["units"].values() for x in us}, reverse=True)
        b.append("  <h2>Unit-wise questions from recent papers</h2>")
        b.append("  <p>Section C questions from the latest papers (%s), sorted by unit. Use these to practise one unit at a time.</p>" % E(", ".join("%s %s" % r for r in recent)))
        for u, qs in g["units"].items():
            items = "".join('<li>%s <small>(%s, <a href="/papers/%s">%s</a>)</small></li>' % (E(q["q"]), E(q["session"]), q["page"], E(q["code"])) for q in qs)
            b.append('  <details class="iq-unit"%s><summary>Unit %s</summary><ul>%s</ul></details>' % (" open" if u == "1" else "", u, items))
    b.append("  <h2>Papers used for this list</h2>")
    b.append("  <ul>%s</ul>" % "".join('<li><a href="/papers/%s">AKTU %s (%s) question paper %s</a></li>' % (p["page"], E(plain), E(p["code"]), E(p["session"])) for p in g["papers"]))
    b.append("  <h2>How to use these questions</h2>")
    b.append("  <ol>\n    <li>Start with the questions asked in the most papers, and make short notes for each.</li>\n    <li>Write 2–3 long answers by hand with a timer (about 12–15 minutes each), then compare them with your textbook.</li>\n    <li>Revise all the 2-mark questions the night before the exam.</li>\n    <li>Finish with one full paper from the list above, timed.</li>\n  </ol>")
    b.append('  <p>Full plan with AI prompts: <a href="/aktu-exam-preparation/">How to prepare for AKTU exams using previous year papers</a>. After results, check your marks with the <a href="/aktu-cgpa-calculator/">AKTU CGPA calculator</a>.</p>')
    faq = [("Are these AKTU %s questions guaranteed to come in the exam?" % plain,
            "No. They are the questions that repeated most in past papers, which makes them a strong hint, but AKTU can ask anything from the syllabus. Use this list to prioritise, not to skip units."),
           ("How was this important questions list made?",
            "We compared all %d questions from %d AKTU %s papers (%s to %s) and grouped questions that ask about the same topic, then counted how many papers each appeared in." % (g["nquestions"], n, plain, oldest, latest)),
           ("Where can I download AKTU %s previous year papers?" % plain,
            "Every paper used here is on LearnAIFast with all questions as text and a link to the original PDF. See the list of papers above.")]
    b.append("  <h2>Frequently asked questions</h2>")
    b.append('  <div class="faq">\n%s\n  </div>' % "\n".join("    <p><b>%s</b><br>%s</p>" % (E(q), E(a)) for q, a in faq))
    b.append('  <p class="next">More subjects: <a href="/important-questions/">all AKTU important questions</a> · <a href="/papers/">all question papers</a></p>')
    path = "/important-questions/%s/" % g["slug"]
    graph = [ORG,
             {"@type": "WebPage", "name": head, "url": SITE + path, "description": desc, "dateModified": TODAY, "inLanguage": "en-IN", "publisher": {"@id": SITE + "/#org"}},
             crumbs_ld([("Home", "/"), ("Papers", "/papers/"), ("Important questions", "/important-questions/"), (head, path)]),
             {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    build(path, title, desc, '<article class="page read" style="max-width:820px">\n%s\n</article>' % "\n".join(b), graph)
    return path, head, n, len(long_rows) + len(short_rows)

made = [page_for(g) for g in G]

# index
cards = "\n".join('    <a class="iq-card" href="%s"><b>%s</b><span>%d papers · %d repeated questions</span></a>' % (p, E(h.replace("AKTU ", "").replace(" Important Questions", "")), n, k) for p, h, n, k in made)
body = """<section class="page">
  <div class="crumbs"><a href="/">Home</a> / <a href="/papers/">Papers</a> / <span>Important questions</span></div>
  <div class="eyebrow">AKTU · Exam prep</div>
  <h1>AKTU Important Questions by Subject</h1>
  <p class="lede">The most repeated questions in AKTU B.Tech and MCA exams, found by comparing every question in our previous year papers. Pick your subject.</p>
  <div class="iq-grid">
%s
  </div>
  <h2>How these lists are made</h2>
  <p>For each subject we compared every question across 4 to 16 previous year papers, grouped questions that ask about the same topic, and counted how many papers each appeared in. Each list shows the years and the different ways a question was worded, with links to the full papers.</p>
  <p>Repeated topics are a strong hint, not a guarantee. Use these lists to decide what to study first, then cover the rest of your syllabus. Our guide on <a href="/aktu-exam-preparation/">preparing for AKTU exams with previous year papers</a> has a 7-day plan.</p>
</section>""" % cards
idx_desc = "Most repeated AKTU B.Tech and MCA exam questions by subject: AI, Machine Learning, NLP, Python, Big Data, Data Analytics and more, from previous year papers."
build("/important-questions/", "AKTU Important Questions by Subject (PYQ-Based)", idx_desc, body,
      [ORG, {"@type": "CollectionPage", "name": "AKTU important questions", "url": SITE + "/important-questions/", "description": idx_desc,
             "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + p, "name": h} for i, (p, h, n, k) in enumerate(made)]}},
       crumbs_ld([("Home", "/"), ("Papers", "/papers/"), ("Important questions", "/important-questions/")])])

# cross-links: each paper page -> its subject's list; papers index; homepage; sitemap
link_for = {}
for g in G:
    for p in g["papers"]: link_for[p["page"]] = ("/important-questions/%s/" % g["slug"], g["name"])
n = 0
for page, (url, name) in link_for.items():
    f = os.path.join(ROOT, "papers", page); s = open(f, encoding="utf-8").read()
    if "/important-questions/" in s: continue
    m = re.search(r'\n  <h2 id="other-years">', s)
    if not m: continue
    s = s[:m.start()] + '\n  <p class="iq-link"><strong>Short on time?</strong> See the <a href="%s">most repeated AKTU %s questions</a> across all years.</p>\n' % (url, E(name.replace("MCA ", ""))) + s[m.start():]
    open(f, "w", encoding="utf-8").write(s); n += 1
print("paper pages linked:", n)

p = os.path.join(ROOT, "papers/index.html"); s = open(p, encoding="utf-8").read()
if "/important-questions/" not in s:
    s = s.replace('  <p>Results out? Work out your SGPA', '  <p><strong>New:</strong> <a href="/important-questions/">AKTU important questions by subject</a>, the most repeated questions across all years.</p>\n  <p>Results out? Work out your SGPA', 1)
    assert "/important-questions/" in s; open(p, "w", encoding="utf-8").write(s)
p = os.path.join(ROOT, "index.html"); s = open(p, encoding="utf-8").read()
if "/important-questions/" not in s:
    s = s.replace('<a href="/papers/">Browse question papers →</a></p>', '<a href="/papers/">Browse question papers →</a> · <a href="/important-questions/">Most repeated questions by subject →</a></p>', 1)
    assert "/important-questions/" in s; open(p, "w", encoding="utf-8").write(s)
p = os.path.join(ROOT, "aktu-exam-preparation/index.html"); s = open(p, encoding="utf-8").read()
if "/important-questions/" not in s:
    s = s.replace("  <h3>Step 2: Find the repeated topics</h3>\n", '  <h3>Step 2: Find the repeated topics</h3>\n  <p><strong>Shortcut:</strong> we\'ve already done this for 19 subjects. See <a href="/important-questions/">AKTU important questions by subject</a>. To do it yourself for any subject:</p>\n', 1)
    assert "/important-questions/" in s; open(p, "w", encoding="utf-8").write(s)

sp = os.path.join(ROOT, "sitemap.xml"); sm = open(sp, encoding="utf-8").read()
urls = ["/important-questions/"] + [m[0] for m in made]
add = "".join("  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (SITE, u, TODAY, "0.8" if u.count("/") > 2 else "0.9") for u in urls if SITE + u + "<" not in sm)
anchor = re.search(r"  <url><loc>%s/papers/</loc>.*?</url>\n" % re.escape(SITE), sm).group(0)
sm = sm.replace(anchor, anchor + add, 1); open(sp, "w", encoding="utf-8").write(sm)
print("pages:", len(made) + 1, "| sitemap urls:", sm.count("<loc>"))
