#!/usr/bin/env python3
"""Pre-render the papers list into papers/index.html so search engines see
plain links to every paper without running JavaScript.

Run after editing papers/data.js:   python3 scripts/papers_index.py
The page's script still re-renders the list for filtering, from the same data.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
js = (ROOT / "papers" / "data.js").read_text(encoding="utf-8")
js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
js = re.sub(r"(?m)^\s*//.*$", "", js)


def arr(name):
    body = re.search(r"window\.%s\s*=\s*(\[.*?\]);" % name, js, re.S).group(1)
    body = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', body)
    body = re.sub(r",\s*([\]}])", r"\1", body)
    return json.loads(body)


S, P = arr("SUBJECTS"), arr("PAPERS")
e = lambda s: html.escape(str(s), quote=True)
out = []
for sub in S:
    items = sorted([p for p in P if p["subject"] == sub], key=lambda p: -p["year"])
    out.append(f'<section class="subject"><div class="subject-head"><h2>{e(sub)}</h2><span class="code">'
               f'{len(items)} paper{"" if len(items) == 1 else "s"}</span></div>')
    if items:
        lis = []
        for p in items:
            ext = not p.get("page")
            lis.append(f'<li><a href="{e(p.get("page") or p["pdf"])}"{" target=\"_blank\" rel=\"noopener\"" if ext else ""}><span class="t">'
                       f'{e(p["university"])} {e(p["course"])} {e(p.get("title") or p["subject"])} {e(p["session"].split(" ")[0])}'
                       f'{"<span class=\"badge pdf\">PDF only</span>" if ext else "<span class=\"badge\">Full paper</span>"}</span>'
                       f'<span class="m">{e(p["code"]) + " · " if p.get("code") else ""}{e(p["semester"])} sem</span></a></li>')
        out.append('<ul class="plist">' + "".join(lis) + "</ul>")
    else:
        out.append('<p class="empty">Papers coming soon. Email us to request one.</p>')
    out.append("</section>")

f = ROOT / "papers" / "index.html"
s = f.read_text(encoding="utf-8")
block = "<!-- LIST:START -->\n" + "\n".join(out) + "\n<!-- LIST:END -->"
if "<!-- LIST:START -->" in s:
    s = re.sub(r"<!-- LIST:START -->.*?<!-- LIST:END -->", lambda m: block, s, flags=re.S)
else:
    s = s.replace('<div id="list"></div>', '<div id="list">' + block + "</div>", 1)
s = re.sub(r'(<p class="count" id="count">)[^<]*', r"\g<1>%d papers" % len(P), s, count=1)
f.write_text(s, encoding="utf-8")
print(f"pre-rendered {len(P)} papers in {len(S)} subjects")
