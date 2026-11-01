#!/usr/bin/env python3
"""Extract every question from learnaifast.in paper pages and find repeats per subject group.
Writes groups.json (one entry per subject page) for the page generator.
Usage: python3 extract.py /home/claude/learnaifast out.json
"""
import json, os, re, subprocess, sys
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT, OUT = sys.argv[1], sys.argv[2]
papers = json.loads(subprocess.check_output(["node", "-e",
    "global.window={};require(process.argv[1]);console.log(JSON.stringify(window.PAPERS))", os.path.join(ROOT, "papers/data.js")]))
papers = [p for p in papers if p.get("page") and os.path.exists(os.path.join(ROOT, "papers", p["page"]))]

# Page groups: (slug, display name, course, [paper titles from data.js])
GROUPS = [
    ("aktu-artificial-intelligence", "Artificial Intelligence", "B.Tech", ["Artificial Intelligence"]),
    ("aktu-big-data", "Big Data", "B.Tech", ["Big Data"]),
    ("aktu-natural-language-processing", "Natural Language Processing", "B.Tech", ["Natural Language Processing"]),
    ("aktu-machine-learning-techniques", "Machine Learning Techniques", "B.Tech", ["Machine Learning Techniques"]),
    ("aktu-python-programming", "Python Programming", "B.Tech", ["Python Programming"]),
    ("aktu-data-analytics", "Data Analytics", "B.Tech", ["Data Analytics"]),
    ("aktu-data-warehousing-data-mining", "Data Warehousing and Data Mining", "B.Tech", ["Data Warehousing & Data Mining", "Data Warehousing and Data Mining"]),
    ("aktu-digital-image-processing", "Digital Image Processing", "B.Tech", ["Digital Image Processing"]),
    ("aktu-image-processing", "Image Processing", "B.Tech", ["Image Processing"]),
    ("aktu-machine-learning", "Machine Learning (Open Elective)", "B.Tech", ["Machine Learning"]),
    ("aktu-application-of-soft-computing", "Application of Soft Computing", "B.Tech", ["Application of Soft Computing"]),
    ("aktu-introduction-to-soft-computing", "Introduction to Soft Computing", "B.Tech", ["Introduction to Soft Computing", "Introduction to Soft Computing (neural Network, Fuzzy Logic and Genetic Algorithm)"]),
    ("aktu-deep-learning", "Deep Learning", "B.Tech", ["Deep Learning"]),
    ("aktu-data-analytics-and-visualization", "Data Analytics and Visualization", "B.Tech", ["Introduction to Data Analytics and Visualization"]),
    ("aktu-big-data-and-analytics", "Big Data and Analytics", "B.Tech", ["Big Data and Analytics"]),
    ("aktu-mca-artificial-intelligence", "MCA Artificial Intelligence", "MCA", ["Artificial Intelligence"]),
    ("aktu-mca-data-warehousing-data-mining", "MCA Data Warehousing and Data Mining", "MCA", ["Data Warehousing & Data Mining"]),
    ("aktu-mca-big-data", "MCA Big Data", "MCA", ["Big Data"]),
    ("aktu-mca-neural-network", "MCA Neural Network", "MCA", ["Neural Network"]),
]

def clean(t):
    return re.sub(r"\s+", " ", t).strip()

def parse(page):
    soup = BeautifulSoup(open(os.path.join(ROOT, "papers", page), encoding="utf-8"), "html.parser")
    main = soup.find("main")
    qs, section, qno = [], None, None
    cq = [h.get_text(strip=True) for h in main.find_all("h3") if re.fullmatch(r"Q\d+", h.get_text(strip=True))]
    modern = cq == ["Q3", "Q4", "Q5", "Q6", "Q7"]
    for el in main.find_all(["h2", "h3", "ol"]):
        if el.name == "h2":
            m = re.match(r"Section ([ABC])", el.get_text(strip=True)); section = m.group(1) if m else None; qno = None
        elif el.name == "h3":
            t = el.get_text(strip=True); qno = t if re.fullmatch(r"Q\d+", t) else qno
        elif el.name == "ol" and "qs" in (el.get("class") or []) and section:
            for li in el.find_all("li", recursive=False):
                for m in li.find_all(class_="marks"): m.decompose()
                text = clean(li.get_text(" "))
                if len(text) < 6: continue
                unit = int(qno[1:]) - 2 if (section == "C" and modern and qno) else None
                qs.append({"text": text, "section": section, "unit": unit})
    return qs

STOP = set("""a an the of in on for to and or with by is are be as at it its this that these those what which how why when where who whom
explain discuss describe define write short note notes brief briefly give list state illustrate elaborate detail details detailed suitable example examples
diagram neat help using use used between difference differentiate compare comparison mean meant term terms concept various different types type
following any two three four five one also their them your you can do does its about role importance advantages disadvantages working work
justify answer statement significance significant main major key basic process steps step method methods technique techniques""".split())

def tokens(t):
    return [w for w in re.findall(r"[a-z][a-z0-9+\-]*", t.lower()) if w not in STOP and len(w) > 1]

def cluster(items, thr):
    docs = [" ".join(tokens(i["text"])) or i["text"].lower() for i in items]
    X = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1).fit_transform(docs)
    S = cosine_similarity(X)
    parent = list(range(len(items)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    # average-linkage style: merge pairs above threshold, but only if the merged clusters stay coherent
    pairs = sorted(((S[i, j], i, j) for i in range(len(items)) for j in range(i + 1, len(items)) if S[i, j] >= thr), reverse=True)
    members = {i: [i] for i in range(len(items))}
    for s, i, j in pairs:
        a, b = find(i), find(j)
        if a == b: continue
        avg = S[[*members[a]]][:, [*members[b]]].mean()
        if avg < thr * 0.9: continue
        parent[b] = a; members[a] += members.pop(b)
    return [m for m in members.values()], S

result = []
for slug, name, course, titles in GROUPS:
    ps = [p for p in papers if p["course"] == course and (p.get("title") or p["subject"]) in titles]
    if len(ps) < 4: continue
    items = []
    for p in ps:
        sess = (p.get("session") or str(p["year"])).split(" ")[0]
        for q in parse(p["page"]):
            q.update(page=p["page"], code=p["code"], session=sess); items.append(q)
    groups_out = {}
    for kind, sel, thr in [("long", lambda q: q["section"] in "BC", 0.46), ("short", lambda q: q["section"] == "A", 0.56)]:
        its = [q for q in items if sel(q)]
        if len(its) < 2: groups_out[kind] = []; continue
        cl, S = cluster(its, thr)
        rows = []
        for m in cl:
            sessions = sorted({its[i]["session"] for i in m}, reverse=True)
            npapers = len({its[i]["page"] for i in m})
            if npapers < 2: continue
            # representative: among the most central members, the shortest clean wording
            best = max(S[i, m].mean() for i in m)
            cands = [i for i in m if S[i, m].mean() >= best - 0.06]
            rep = min(cands, key=lambda i: (bool(re.search(r"\b\d{1,2}\s*$|\s\d{1,2}\s", its[i]["text"])), len(its[i]["text"])))
            units = [its[i]["unit"] for i in m if its[i]["unit"]]
            unit = max(set(units), key=units.count) if units else None
            seen, variants = {re.sub(r"\W+", "", its[rep]["text"].lower())[:60]}, []
            for i in sorted(m, key=lambda i: len(its[i]["text"])):
                k = re.sub(r"\W+", "", its[i]["text"].lower())[:60]
                if k not in seen: seen.add(k); variants.append(its[i]["text"])
            rows.append({"q": its[rep]["text"], "times": npapers, "sessions": sessions, "unit": unit,
                         "variants": variants[:3],
                         "papers": sorted({(its[i]["session"], its[i]["code"], its[i]["page"]) for i in m}, reverse=True)})
        rows.sort(key=lambda r: (-r["times"], r["q"]))
        groups_out[kind] = rows
    # unit-wise Section C questions from the 3 most recent papers that use the 5-unit pattern
    modern_pages = []
    for page in sorted({q["page"] for q in items if q["unit"]}, key=lambda pg: next(q["session"] for q in items if q["page"] == pg), reverse=True)[:3]:
        modern_pages.append(page)
    units = {}
    for q in items:
        if q["unit"] and q["page"] in modern_pages:
            units.setdefault(q["unit"], []).append({"q": q["text"], "session": q["session"], "code": q["code"], "page": q["page"]})
    for u in units: units[u].sort(key=lambda x: x["session"], reverse=True)
    groups_out["units"] = {str(k): units[k] for k in sorted(units)}
    result.append({"slug": slug, "name": name, "course": course, "codes": sorted({p["code"] for p in ps}),
                   "papers": sorted([{"session": (p.get("session") or str(p["year"])).split(" ")[0], "code": p["code"], "page": p["page"], "sem": p.get("semester", "")} for p in ps], key=lambda x: x["session"], reverse=True),
                   "nquestions": len(items), **groups_out})
    print(f"{slug:42} papers={len(ps):2} qs={len(items):3} long_repeats={len(groups_out['long']):3} short_repeats={len(groups_out['short']):3}")
json.dump(result, open(OUT, "w"), indent=1, ensure_ascii=False)
