#!/usr/bin/env python3
"""Write today's Daily AI Update with the Gemini API, then publish it with daily.py.

Runs without Claude, e.g. from GitHub Actions (.github/workflows/daily.yml).
Needs only the Python standard library and one secret:

    GEMINI_API_KEY   your key from https://aistudio.google.com/apikey
    GEMINI_MODEL     optional, default "gemini-3.8-flash"
    DRY_RUN=1        optional, write the JSON but do not publish

Steps:
  1. Stop if today's post (IST date) already exists in daily/posts.json.
  2. Research: Gemini + Google Search finds recent AI news. We keep only the
     real web pages Google's search returned (grounding sources).
  3. Write: Gemini turns those findings into the JSON format daily.py expects,
     using ONLY the verified source links.
  4. Check every field (lengths, sources, no repeats) and drop weak items.
     If fewer than 3 good items remain, retry; after 3 tries, exit with an
     error so GitHub emails you and nothing half-done is published.
  5. Run scripts/daily.py to build the pages.
"""
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "daily" / "posts.json"
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
KEY = os.environ.get("GEMINI_API_KEY", "")
UA = "Mozilla/5.0 (compatible; LearnAIFastBot/1.0; +https://learnaifast.in)"

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def gemini(prompt, search=False, json_out=False, temperature=0.4):
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    if search:
        body["tools"] = [{"google_search": {}}]
    if json_out:
        body["generationConfig"]["responseMimeType"] = "application/json"
    req = urllib.request.Request(
        API.format(model=MODEL), data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:500]
            if e.code in (429, 500, 503) and attempt < 3:
                log(f"Gemini {e.code}, retrying in {20 * (attempt + 1)}s: {msg}")
                time.sleep(20 * (attempt + 1))
                continue
            sys.exit(f"Gemini API error {e.code}: {msg}")
    cand = (data.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    chunks = (cand.get("groundingMetadata") or {}).get("groundingChunks") or []
    return text, [c["web"] for c in chunks if c.get("web", {}).get("uri")]


def resolve(url):
    """Follow Google's grounding redirect to the real article URL; None if it doesn't load."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            if r.status < 400:
                return r.geturl()
    except Exception as e:  # noqa: BLE001 - any failure means "not usable"
        log("  source failed:", url[:90], type(e).__name__)
    return None


def clean_url(u):
    return re.sub(r"[?#].*$", "", u.rstrip("/")) if u else u


def recent(posts, days=14, today=None):
    cutoff = (today - dt.timedelta(days=days)).isoformat()
    return [n["headline"] for p in posts if p["date"] >= cutoff for n in p["news"]]


def research(today, avoid):
    prompt = f"""Today is {today:%d %B %Y} (India time). Use Google Search to find 6-8 AI news
stories published in the last 48 hours that a beginner in India would care about.

Priority: new free features in ChatGPT, Gemini, Claude, Copilot, Meta AI, WhatsApp and other
tools people actually use; India news (government AI schemes, IndiaAI, fellowships, exams,
jobs, Indian startups, Indian-language AI); big model launches explained simply; AI scam
and safety warnings. Skip investor, stock market and funding stories.

Do NOT include these stories, which we already covered:
{chr(10).join('- ' + h for h in avoid) or '- (none)'}

For each story give: headline, date published, publisher, and 4-6 factual sentences with the
key names, numbers and dates exactly as the source states them. Only include facts you found
in search results today. Prefer official and original sources."""
    text, sources = gemini(prompt, search=True, temperature=0.2)
    real = {}
    for s in sources:
        u = resolve(s["uri"])
        if u and "vertexaisearch" not in u and "google.com/search" not in u:
            real[clean_url(u)] = s.get("title") or ""
    log(f"research: {len(text)} chars, {len(sources)} sources, {len(real)} usable")
    return text, real


def write(today, notes, sources, recent_tips):
    src_list = "\n".join(f"- {u}  ({t})" for u, t in sources.items())
    prompt = f"""You write the "Daily AI Update" for learnaifast.in (brand: LearnAIFast).
Readers: students, job seekers and small business owners in India, beginners.
Plain simple English, short sentences, friendly, no hype, no clickbait,
no financial or medical advice.

Research notes (only facts you may use):
{notes}

Verified source links (source_url MUST be copied exactly from this list):
{src_list}

Recent "prompt of the day" titles (pick a different theme):
{chr(10).join('- ' + t for t in recent_tips)}

Return ONLY a JSON object with exactly these keys:
{{
  "date": "{today.isoformat()}",
  "title": "50-70 characters, keyword first, main story first, e.g. 'ChatGPT Adds X, Gemini Gets Y and More'",
  "summary": "120-160 characters, starting with: Today's AI news in simple words:",
  "intro": "1-2 friendly sentences",
  "news": [
    {{"headline": "short, clear, factual",
      "body": "60-110 words in your own words. Do not copy sentences from sources.",
      "why": "1-2 sentences: what it means for a student, job seeker or small business in India",
      "source_name": "publisher name",
      "source_url": "one URL from the verified list"}}
  ],
  "tip": {{"title": "prompt of the day title", "body": "1-2 sentences",
           "prompt": "a copyable prompt with [placeholders], tied to one story"}},
  "tags": ["5-7 short tags, no spaces"]
}}
Use 3-4 news items. Each must match its source link. Never invent facts, numbers or quotes.
If a fact is not in the notes, leave it out. Rotate tip themes: study, exam prep,
career/resume, small business, daily life, Hindi/Hinglish."""
    text, _ = gemini(prompt, json_out=True, temperature=0.5)
    text = re.sub(r"^```(?:json)?|```$", "", text.strip()).strip()
    return json.loads(text)


def check(post, today, sources, avoid):
    """Return (post, problems). Drops news items that fail; fixes small issues."""
    problems = []
    allowed = set(sources)
    seen_headlines = {h.lower() for h in avoid}
    good = []
    for n in post.get("news", []):
        u = clean_url(n.get("source_url", ""))
        words = len(str(n.get("body", "")).split())
        if not all(n.get(k) for k in ("headline", "body", "why", "source_name", "source_url")):
            problems.append(f"missing field in: {n.get('headline')}")
        elif u not in allowed:
            problems.append(f"unverified source: {u}")
        elif not 45 <= words <= 140:
            problems.append(f"body length {words}: {n['headline']}")
        elif n["headline"].lower() in seen_headlines:
            problems.append(f"repeat: {n['headline']}")
        else:
            n["source_url"] = next(s for s in sources if clean_url(s) == u)
            good.append(n)
    post["news"] = good[:4]
    post["date"] = today.isoformat()
    for k in ("title", "summary", "intro", "tip"):
        if not post.get(k):
            problems.append(f"missing {k}")
    t = post.get("title", "")
    if not 35 <= len(t) <= 80:
        problems.append(f"title length {len(t)}")
    s = post.get("summary", "")
    if not s.startswith("Today's AI news in simple words:"):
        post["summary"] = "Today's AI news in simple words: " + s
    if len(post["summary"]) > 170:
        post["summary"] = post["summary"][:167].rsplit(" ", 1)[0] + "..."
    tip = post.get("tip") or {}
    if not all(tip.get(k) for k in ("title", "body", "prompt")):
        problems.append("tip incomplete")
    post["tags"] = [re.sub(r"\s+", "", str(x)) for x in post.get("tags", [])][:7] or ["AINews"]
    return post, problems


def main():
    if not KEY:
        sys.exit("GEMINI_API_KEY is not set (add it in GitHub: Settings > Secrets and variables > Actions).")
    today = dt.datetime.now(IST).date()
    posts = json.loads(POSTS.read_text(encoding="utf-8")) if POSTS.exists() else []
    if any(p["date"] == today.isoformat() for p in posts):
        print(f"already published for {today}")
        return
    avoid = recent(posts, today=today)
    recent_tips = [p["tip"]["title"] for p in posts[:6]]

    for attempt in range(1, 4):
        log(f"--- attempt {attempt} ({MODEL})")
        notes, sources = research(today, avoid)
        if len(sources) < 3:
            log("not enough usable sources")
            continue
        try:
            post = write(today, notes, sources, recent_tips)
        except (json.JSONDecodeError, ValueError) as e:
            log("bad JSON from Gemini:", e)
            continue
        post, problems = check(post, today, sources, avoid)
        for p in problems:
            log("  check:", p)
        hard = [p for p in problems if p.startswith(("missing", "tip", "title"))]
        if len(post["news"]) >= 3 and not hard:
            break
    else:
        sys.exit("Could not produce a good post after 3 tries; nothing was published.")

    out = ROOT / "daily" / "_data" / f"{today.isoformat()}.json"
    out.write_text(json.dumps(post, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log("wrote", out.relative_to(ROOT))
    if os.environ.get("DRY_RUN"):
        print(json.dumps(post, indent=2, ensure_ascii=False))
        return
    subprocess.run([sys.executable, str(ROOT / "scripts" / "daily.py"), str(out)], check=True)


if __name__ == "__main__":
    main()
