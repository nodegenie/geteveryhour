#!/usr/bin/env python3
"""Build the EveryHour static site from posts/*.json into _site/.

No third-party packages needed. Run: python3 build.py
"""
import html
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import og

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
CFG = json.loads((ROOT / "config.json").read_text())
TZ = ZoneInfo(CFG["timezone"])
SITE = CFG["site_url"].rstrip("/")
AUTHOR = CFG["author"]
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700"
         "&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400"
         "&family=IBM+Plex+Mono:wght@400;500&display=swap")

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
STATS = {}  # filled in build(): day number, posts, sources, sponsors


def goat_code():
    return (CFG.get("goatcounter") or "").strip()


def visitors_script():
    """GoatCounter: counts page views without cookies."""
    code = goat_code()
    if not code:
        return ""
    return f'<script data-goatcounter="https://{e(code)}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'


def analytics_panel(posts):
    """Readership from GoatCounter's public counters: total visits and the most-read posts, fetched live."""
    code = goat_code()
    if not code:
        return ""
    items = [{"p": p["path"], "t": p["title"], "h": hour_label(p["local"]).replace("\u2009", " "), "d": f"{p['local']:%b} {p['local'].day}"} for p in posts[:150]]
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    base = f"https://{e(code)}.goatcounter.com/counter/"
    return f"""<section class="analytics" aria-labelledby="an-h">
  <h2 id="an-h" class="day" style="color:var(--ink)">Readership</h2>
  <div class="an-row"><div class="stat"><small>Total visits</small><b id="an-total">&ndash;</b><span>all pages, counted without cookies</span></div>
  <div class="stat"><small>Posts with readers</small><b id="an-read">&ndash;</b><span id="an-of">of the latest {len(items)} posts</span></div></div>
  <h3 class="an-sub">Most-read posts</h3>
  <ol class="an-list" id="an-list"><li class="an-empty">Loading visit counts&hellip;</li></ol>
  <p class="an-note" id="an-note" hidden>Visit counts are not available yet. In GoatCounter, open Settings and turn on &ldquo;Allow adding visitor counts on your website.&rdquo;</p>
</section>
<script>(()=>{{const P={data},B="{base}",L=document.getElementById("an-list");
const num=n=>Number(String(n).replace(/[^0-9]/g,""))||0;
const get=u=>fetch(B+encodeURIComponent(u)+".json").then(r=>r.ok?r.json():null).catch(()=>null);
get("TOTAL").then(j=>{{if(j)document.getElementById("an-total").textContent=j.count;else document.getElementById("an-note").hidden=false}});
const out=[];let i=0;const next=()=>{{if(i>=P.length)return Promise.resolve();const it=P[i++];return get(it.p).then(j=>{{if(j)out.push({{...it,n:num(j.count)}})}}).then(next)}};
Promise.all(Array.from({{length:6}},next)).then(()=>{{const r=out.filter(x=>x.n>0).sort((a,b)=>b.n-a.n);
document.getElementById("an-read").textContent=r.length;
L.innerHTML="";if(!r.length){{L.innerHTML='<li class="an-empty">No visits recorded on posts yet.</li>';return}}
r.slice(0,15).forEach(x=>{{const li=document.createElement("li");const a=document.createElement("a");a.href=x.p;a.textContent=x.t;
const m=document.createElement("span");m.className="an-meta";m.textContent=x.d+", "+x.h;const c=document.createElement("b");c.textContent=x.n.toLocaleString()+(x.n==1?" visit":" visits");
li.append(a,m,c);L.append(li)}})}})}})();</script>"""


def fetch_locations(since):
    """Visit counts by country and region from the GoatCounter API (needs GOATCOUNTER_TOKEN; the key stays on the build server)."""
    token, code = os.environ.get("GOATCOUNTER_TOKEN", "").strip(), goat_code()
    if not token or not code:
        return None
    api = f"https://{code}.goatcounter.com/api/v0/stats/locations"
    q = urllib.parse.urlencode({"start": since.strftime("%Y-%m-%d"), "end": (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d"), "limit": 100})

    def get(url):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode()).get("stats") or []

    try:
        countries = [c for c in get(f"{api}?{q}") if int(c.get("count") or 0) > 0 and c.get("id")]
        out = []
        for c in countries[:40]:
            regions = []
            try:
                time.sleep(0.3)  # API allows 4 requests a second
                regions = [r for r in get(f"{api}/{urllib.parse.quote(c['id'])}?{q}") if int(r.get("count") or 0) > 0]
            except Exception:
                pass
            out.append({"id": c["id"], "name": c.get("name") or c["id"], "count": int(c["count"]),
                        "regions": [{"id": r.get("id") or "", "name": r.get("name") or "", "count": int(r["count"])} for r in regions]})
        return out
    except Exception as ex:
        print("location stats unavailable:", ex, file=sys.stderr)
        return None


def map_panel(locs):
    """A world map with one dot per place readers came from (region when known, otherwise country)."""
    if locs is None:
        return ""
    geo = json.loads((ROOT / "assets" / "map-points.json").read_text())
    pts, W, H = geo["points"], geo["w"], geo["h"]
    dots = []  # (x, y, label, count)
    for c in locs:
        placed = 0
        for r in c["regions"]:
            p = pts.get(r["id"])
            if p and r["id"] != c["id"]:
                label = f"{r['name']}, {c['name']}" if r["name"] else c["name"]
                dots.append((p[0], p[1], label, r["count"])); placed += r["count"]
        rest = c["count"] - placed
        if rest > 0 and c["id"] in pts:
            dots.append((pts[c["id"]][0], pts[c["id"]][1], c["name"], rest))
    dots.sort(key=lambda d: -d[3])
    total = sum(d[3] for d in dots)
    circles = "".join(
        f'<circle cx="{x}" cy="{y}" r="{7 + 4 * n ** 0.5:.1f}"><title>{e(lbl)}: {n:,} {"visit" if n == 1 else "visits"}</title></circle>'
        for x, y, lbl, n in reversed(dots))
    rows = "".join(f'<li><span>{e(lbl)}</span><b>{n:,}</b></li>' for _, _, lbl, n in dots[:12])
    summary = (f"{total:,} {'visit' if total == 1 else 'visits'} from {len(dots)} {'place' if len(dots) == 1 else 'places'}"
               + "." if dots else "No locations recorded yet.")
    return f"""<section class="geo" aria-labelledby="geo-h">
  <h2 id="geo-h" class="day" style="color:var(--ink)">Where readers are</h2>
  <p class="an-note" style="margin-top:4px">{summary} Places are approximate (country or state) and updated every hour.</p>
  <div class="geo-map"><img src="/assets/world-map.svg" alt="" width="{W}" height="{H}"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Map of reader locations: {e(summary)}">{circles}</svg></div>
  {f'<ol class="geo-list">{rows}</ol>' if rows else ''}
</section>"""


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return s[:60].strip("-") or "post"


# ---------- load posts ----------
REQUIRED = ["title", "dek", "topic", "publishedAt", "body"]


def load_posts():
    posts, errors = [], []
    for f in sorted((ROOT / "posts").glob("*.json")):
        try:
            p = json.loads(f.read_text())
            missing = [k for k in REQUIRED if not p.get(k)]
            if missing:
                raise ValueError("missing " + ", ".join(missing))
            p["dt"] = datetime.fromisoformat(p["publishedAt"].replace("Z", "+00:00")).astimezone(timezone.utc)
            p["local"] = p["dt"].astimezone(TZ)
            p["slug"] = slugify(p.get("slug") or p["title"])
            if isinstance(p["body"], str):
                p["body"] = [x.strip() for x in re.split(r"\n\s*\n", p["body"]) if x.strip()]
            p["path"] = f"/{p['local']:%Y/%m/%d}/{p['slug']}/"
            p["url"] = SITE + p["path"]
            p["topic_slug"] = slugify(p["topic"])
            p["tags"] = p.get("tags") or []
            p["keywords"] = p.get("keywords") or p["tags"]
            p["readMin"] = p.get("readMin") or max(1, round(sum(len(x.split()) for x in p["body"]) / 230))
            if p["dt"] > datetime.now(timezone.utc):  # scheduled for a later hour: publish when its hour arrives
                continue
            kp = p.get("keyPoints") or []
            p["keyPoints"] = [str(x).strip() for x in kp if str(x).strip()][:5] if isinstance(kp, list) else []
            src = p.get("sources") or []
            p["sources"] = [{"title": str(x.get("title") or x["url"]).strip(), "url": x["url"].strip()}
                            for x in src if isinstance(x, dict) and str(x.get("url", "")).startswith(("http://", "https://"))][:5] if isinstance(src, list) else []
            s = p.get("sponsor")
            if s and not (s.get("name") and str(s.get("url", "")).startswith(("http://", "https://"))):
                p["sponsor"] = None
            posts.append(p)
        except Exception as ex:  # a bad file should not take the site down
            errors.append(f"{f.name}: {ex}")
    posts.sort(key=lambda p: p["dt"], reverse=True)
    # de-duplicate paths
    seen = set()
    for p in posts:
        base, n = p["path"], 2
        while p["path"] in seen:
            p["path"] = base.rstrip("/") + f"-{n}/"; n += 1
        p["url"] = SITE + p["path"]
        seen.add(p["path"])
    return posts, errors


# ---------- helpers ----------
def hour_label(d):
    h = d.hour % 12 or 12
    return f"{h} {'AM' if d.hour < 12 else 'PM'}"


def long_date(d):
    return f"{d:%A}, {d:%B} {d.day}"


def day_label(d, now):
    if d.date() == now.date():
        return "Today"
    if d.date() == (now - timedelta(days=1)).date():
        return "Yesterday"
    return long_date(d)


def write(rel, text):
    path = OUT / rel.lstrip("/")
    if rel.endswith("/"):
        path = path / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def signup_block():
    n = CFG.get("newsletter", {})
    user = (n.get("username") or "").strip()
    if not user:
        return ""
    action = f"https://buttondown.com/api/emails/embed-subscribe/{e(user)}"
    return f"""<section class="signup" id="subscribe" aria-labelledby="signup-h">
  <h2 id="signup-h">Get EveryHour in your inbox</h2>
  <p>Leave your email address and I will send you new EveryHour posts. You can unsubscribe at any time.</p>
  <form action="{action}" method="post">
    <label for="bd-email">Email address</label>
    <input type="email" name="email" id="bd-email" placeholder="you@example.com" required autocomplete="email">
    <input type="hidden" name="tag" value="website">
    <button type="submit">Subscribe</button>
  </form>
</section>"""


def sponsor_box(p):
    s = p.get("sponsor")
    if not s:
        return ""
    blurb = f"<p>{e(s.get('blurb'))}</p>" if s.get("blurb") else ""
    return f"""<aside class="sponsor" aria-label="Sponsor">
  <div class="sponsor-label">Sponsored</div>
  <a class="sponsor-name" href="{e(s['url'])}" rel="sponsored noopener" target="_blank">{e(s['name'])}</a>
  {blurb}
  <small>This hour is sponsored by {e(s['name'])}. <a href="/sponsor/">Feature your business</a></small>
</aside>"""


def page(title, desc, canonical, body, *, og_type="website", jsonld=None, extra_head="", noindex=False, image="/og/home.png"):
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    gsv = CFG.get("google_site_verification", "").strip()
    if gsv:  # Google Search Console URL-prefix verification (config.json)
        robots += f'\n<meta name="google-site-verification" content="{e(gsv)}">'
    bsv = CFG.get("bing_site_verification", "").strip()
    if bsv:  # Bing Webmaster Tools verification (config.json)
        robots += f'\n<meta name="msvalidate.01" content="{e(bsv)}">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="author" content="{e(AUTHOR)}">
{robots}
<link rel="canonical" href="{e(canonical)}">
<link rel="alternate" type="application/rss+xml" title="{e(CFG['title'])}" href="{SITE}/feed.xml">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:site_name" content="{e(CFG['title'])}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}{image}">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
{extra_head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
<header class="site">
  <a class="brand" href="/"><b>{e(CFG['title'])}</b><span>{e(CFG['tagline'])}</span></a>
  <nav class="top" aria-label="Site"><a href="/archive/">Archive</a><a href="/stats/">Stats</a><a href="/about/">About</a><a href="/sponsor/">Sponsor</a>{'<a href="#subscribe">Subscribe</a>' if signup_block() else ''}</nav>
</header>
<main id="main">
{body}
</main>
{signup_block()}
<section class="author">
  <div class="avatar" aria-hidden="true">{e(''.join(w[0] for w in AUTHOR.split()[:2]))}</div>
  <div><b>{e(AUTHOR)}</b><p>{e(CFG['author_bio'])}</p></div>
</section>
<footer class="site">
  <span>&copy; {datetime.now(TZ).year} {e(AUTHOR)}</span>
  <a href="/feed.xml">RSS</a><a href="/sitemap.xml">Sitemap</a>
  {f'<a href="/stats/">Day {STATS["day"]} &middot; {STATS["posts"]} posts</a>' if STATS else ''}
  <span>A new post every hour, Pacific time. Posts are <a href="/about/#how-posts-are-made">written with AI</a>.</span>
</footer>
</div>
{visitors_script()}
</body>
</html>
"""


def item_html(p):
    return (f'<a class="item" href="{p["path"]}"><span class="hr">{hour_label(p["local"])}</span>'
            f'<div><h3>{e(p["title"])}</h3><p>{e(p["dek"])}</p></div></a>')


def grouped_list(posts, now):
    out, last = [], None
    for p in posts:
        dl = day_label(p["local"], now)
        if dl != last:
            out.append(f'<h2 class="day">{e(dl)}</h2>')
            last = dl
        out.append(item_html(p))
    return '<div class="list">' + "".join(out) + "</div>"


def dial(posts, now):
    on = {p["local"].hour for p in posts if p["local"].date() == now.date()}
    cells = "".join(f'<i class="{"on" if h in on else ""}" title="{(h % 12) or 12} {"AM" if h < 12 else "PM"}"></i>' for h in range(24))
    return f"""<section class="dial" aria-label="Posts today">
  <div class="dial-head"><span>{e(now.strftime('%a, %b'))} {now.day} &middot; {len(on)} of 24 hours</span><span>Pacific time</span></div>
  <div class="hours">{cells}</div>
  <div class="hours-ticks"><span>12 AM</span><span>6 AM</span><span>Noon</span><span>6 PM</span></div>
</section>"""


def topic_chips(topics, current=None):
    chips = [f'<a class="chip{" on" if current is None else ""}" href="/">All</a>']
    for slug, name in topics:
        chips.append(f'<a class="chip{" on" if slug == current else ""}" href="/topics/{slug}/">{e(name)}</a>')
    return '<nav class="topics" aria-label="Topics">' + "".join(chips) + "</nav>"


def person():
    return {"@type": "Person", "name": AUTHOR, "url": SITE + "/about/"}


# ---------- build ----------
def build():
    posts, errors = load_posts()
    for err in errors:
        print("skipped", err, file=sys.stderr)
    now = datetime.now(TZ)
    launch = datetime.fromisoformat(CFG["launch_at"]).astimezone(TZ) if CFG.get("launch_at") else (posts[-1]["local"] if posts else now)
    STATS.update({
        "launch": launch,
        "day": max(1, (now.date() - launch.date()).days + 1),
        "hours": max(0, int((now - launch).total_seconds() // 3600)),
        "posts": len(posts),
        "sources": sum(len(p["sources"]) for p in posts),
        "words": sum(sum(len(x.split()) for x in p["body"]) for p in posts),
        "sponsors": 0,
    })
    try:
        q = json.loads((ROOT / "sponsors" / "queue.json").read_text())
        STATS["sponsors"] = sum(1 for x in q if x.get("placedIn"))
    except Exception:
        pass

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "CNAME").write_text(CFG["domain"] + "\n")
    og.card(OUT / "og" / "home.png", "Relatable thoughts on what the world is talking about, every hour.", CFG["tagline"])
    og.card(OUT / "og" / "sponsor.png", f"Feature your business on EveryHour for {CFG.get('sponsor', {}).get('price', '$5')}", "Sponsor an hour")
    (OUT / ".nojekyll").write_text("")

    counts = {}
    for p in posts:
        counts.setdefault(p["topic_slug"], [p["topic"], 0])[1] += 1
    topics = [(s, v[0]) for s, v in sorted(counts.items(), key=lambda kv: -kv[1][1])]

    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": CFG["title"], "url": SITE + "/",
               "description": CFG["description"], "author": person(), "publisher": person()}

    # home
    if posts:
        lead, rest = posts[0], posts[1:CFG["home_post_count"]]
        body = dial(posts, now) + f"""
<section class="lead">
  <div class="eyebrow">Latest &middot; <a href="/topics/{lead['topic_slug']}/">{e(lead['topic'])}</a></div>
  <h1><a class="t" href="{lead['path']}">{e(lead['title'])}</a></h1>
  <p class="dek">{e(lead['dek'])}</p>
  <div class="meta"><span>{e(day_label(lead['local'], now))}, {hour_label(lead['local'])}</span><span class="sep"></span><span>{e(AUTHOR)}</span><span class="sep"></span><span>{lead['readMin']} min read</span></div>
</section>
{topic_chips(topics)}
{grouped_list(rest, now)}
{'<p class="more"><a href="/archive/">See every post in the archive</a></p>' if len(posts) > CFG['home_post_count'] else ''}"""
    else:
        body = dial(posts, now) + '<p class="pagedek" style="margin-top:32px">The first post is on its way.</p>'
    write("/", page(f"{CFG['title']} by {AUTHOR}: relatable thoughts, every hour", CFG["description"], SITE + "/", body, jsonld=[site_ld]))

    # posts
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        related = [q for q in posts if q is not p and q["topic_slug"] == p["topic_slug"]][:4]
        paras = "".join(f"<p>{e(x)}</p>" for x in p["body"])
        keybox = ""
        if p["keyPoints"]:
            keybox = ('<aside class="keypoints" aria-label="What to know"><h2>What to know</h2><ul>'
                      + "".join(f"<li>{e(x)}</li>" for x in p["keyPoints"]) + "</ul></aside>")
        srcs = ""
        if p["sources"]:
            srcs = ('<section class="sources"><h2>Sources</h2><ul>'
                    + "".join(f'<li><a href="{e(x["url"])}" rel="noopener" target="_blank">{e(x["title"])}</a></li>' for x in p["sources"])
                    + '</ul><p>Facts were checked against these sources when the post was written. Details can change, so check them for the latest.</p></section>')
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in p["tags"])
        np = ""
        if older:
            np += f'<a class="older" href="{older["path"]}"><small>Previous hour</small><span>{e(older["title"])}</span></a>'
        if newer:
            np += f'<a class="newer" href="{newer["path"]}"><small>Next hour</small><span>{e(newer["title"])}</span></a>'
        rel = ""
        if related:
            rel = '<section class="related"><h2>More on ' + e(p["topic"]) + '</h2><div class="list">' + "".join(item_html(q) for q in related) + "</div></section>"
        body = f"""<article class="post">
  <div class="crumbs"><a href="/">EveryHour</a> / <a href="/topics/{p['topic_slug']}/">{e(p['topic'])}</a></div>
  <div class="eyebrow">{e(p['topic'])}</div>
  <h1>{e(p['title'])}</h1>
  <p class="dek">{e(p['dek'])}</p>
  <div class="meta"><span>By <a href="/about/" rel="author">{e(AUTHOR)}</a></span><span class="sep"></span><a href="/about/#how-posts-are-made">Written with AI</a><span class="sep"></span><time datetime="{p['dt'].isoformat()}">{e(long_date(p['local']))}, {hour_label(p['local'])}</time><span class="sep"></span><span>{p['readMin']} min read</span></div>
  {keybox}
  <div class="body">{paras}</div>
  {srcs}
  {'<div class="tags">' + tags + '</div>' if tags else ''}
  {sponsor_box(p)}
  <nav class="nextprev" aria-label="More posts">{np}</nav>
  {rel}
</article>"""
        ld = [{
            "@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["dek"],
            "datePublished": p["dt"].isoformat(), "dateModified": p["dt"].isoformat(),
            "mainEntityOfPage": p["url"], "url": p["url"], "articleSection": p["topic"],
            "keywords": ", ".join(p["keywords"]), "wordCount": sum(len(x.split()) for x in p["body"]),
            "author": person(), "publisher": person(), "inLanguage": "en-US",
            **({"citation": [x["url"] for x in p["sources"]]} if p["sources"] else {}),
        }, {
            "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": CFG["title"], "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": p["topic"], "item": f"{SITE}/topics/{p['topic_slug']}/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": p["url"]},
            ]}]
        head = (f'<meta property="article:published_time" content="{p["dt"].isoformat()}">'
                f'<meta property="article:author" content="{e(AUTHOR)}">'
                f'<meta property="article:section" content="{e(p["topic"])}">'
                f'<meta name="keywords" content="{e(", ".join(p["keywords"]))}">')
        img = "/og" + p["path"].rstrip("/") + ".png"
        og.card(OUT / img.lstrip("/"), p["title"], f"{p['topic']} · {p['local']:%A} {hour_label(p['local']).replace(chr(8201), ' ')}")
        ld[0]["image"] = SITE + img
        write(p["path"], page(f"{p['title']} | {CFG['title']}", p["dek"], p["url"], body, og_type="article", jsonld=ld, extra_head=head, image=img))

    # topics
    for slug, name in topics:
        tp = [p for p in posts if p["topic_slug"] == slug]
        body = (f'<h1 class="page">{e(name)}</h1><p class="pagedek">{len(tp)} post{"s" if len(tp) != 1 else ""} about {e(name.lower())} from {e(AUTHOR)}.</p>'
                + topic_chips(topics, slug) + grouped_list(tp, now))
        write(f"/topics/{slug}/", page(f"{name} | {CFG['title']} by {AUTHOR}", f"Relatable, hourly thoughts on {name.lower()} by {AUTHOR}.", f"{SITE}/topics/{slug}/", body))

    # archive
    body = f'<h1 class="page">Archive</h1><p class="pagedek">All {len(posts)} posts, newest first.</p>' + grouped_list(posts, now)
    write("/archive/", page(f"Archive | {CFG['title']}", f"Every EveryHour post by {AUTHOR}, newest first.", SITE + "/archive/", body))

    # about
    body = f"""<h1 class="page">About EveryHour</h1>
<div class="post"><div class="body" style="border:0;padding-top:12px">
<p>EveryHour is a small daily publication by {e(AUTHOR)}. Every hour, a new short post goes up about something people are talking about that day. Some posts are about the news, some are about work or money, and some are about the ordinary parts of a day that everyone recognizes.</p>
<p>Each post is meant to take a minute or two to read and to leave you with one practical thought you can use.</p>
<p>Posts are published on Pacific time. You can follow along here, through the <a href="/feed.xml">RSS feed</a>, or by email.</p>
<h2 id="how-posts-are-made">How posts are made</h2>
<p>EveryHour is written with AI. Each morning, an AI system searches for what people are talking about that day, including news, sports, weather, culture and observances, and writes that day's posts following a set of written guidelines. The posts are then scheduled so that one appears each hour.</p>
<p>{e(AUTHOR)} created EveryHour, wrote the guidelines the posts follow, and is responsible for everything the site publishes. The guidelines require that posts only state facts found in search results at the time of writing, stay away from partisan opinions, and never invent personal stories or experiences. Posts include a short What to know summary and link to the sources their facts were checked against.</p>
<p>AI can still get things wrong, and news can change after a post is written. Please treat posts as short reflections, not professional advice, and check anything important with a trusted source.</p>
<p>Sponsored posts are clearly labeled, and sponsors do not choose or review what a post says.</p>
{'<p>Visits are counted with <a href="https://www.goatcounter.com/">GoatCounter</a>, which does not use cookies or collect personal data. The totals are public on the <a href="/stats/">stats page</a>.</p>' if goat_code() else ''}
</div></div>"""
    about_ld = {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": person()}
    write("/about/", page(f"About | {CFG['title']}", f"About EveryHour and its writer, {AUTHOR}.", SITE + "/about/", body, jsonld=[about_ld]))

    # stats: public, build-in-public numbers (visitors filled live from GoatCounter)
    st = STATS
    tiles = [
        ("Day", f"{st['day']}", f"live since {long_date(st['launch'])}, {st['launch'].year}"),
        ("Posts published", f"{st['posts']:,}", f"in {st['hours']:,} hours since launch"),
        ("Sources cited", f"{st['sources']:,}", "links to the pages facts were checked against"),
        ("Words written", f"{st['words']:,}", "all written with AI"),
        ("Sponsored hours", f"{st['sponsors']:,}", '<a href="/sponsor/">sponsor an hour</a>'),
    ]
    grid = "".join(f'<div class="stat"><small>{e(k)}</small><b>{v}</b><span>{d}</span></div>' for k, v, d in tiles)
    body = f"""<h1 class="page">EveryHour in numbers</h1>
<p class="pagedek">Built in public. These numbers update every hour; visits update live.</p>
<div class="stats">{grid}</div>
{analytics_panel(posts)}
{map_panel(fetch_locations(st['launch']))}
<p class="pagedek" style="margin-top:24px">Updated {e(long_date(now))}, {hour_label(now)} Pacific.</p>"""
    write("/stats/", page(f"Stats | {CFG['title']}", f"EveryHour in numbers: day {st['day']}, {st['posts']} posts published, visits and sponsors, updated every hour.", SITE + "/stats/", body))

    # sponsor page
    sp = CFG.get("sponsor", {})
    link = (sp.get("payment_link") or "").strip()
    price = sp.get("price", "$5")
    cta = (f'<p><a class="sponsor-cta" href="{e(link)}" rel="noopener">Sponsor an hour for {e(price)}</a></p>'
           if link else '<p class="pagedek"><strong>Sponsorships open soon.</strong></p>')
    body = f"""<p class="sponsor" id="paid-note" hidden><strong>Thank you. Your payment went through.</strong> Your business will appear in one of the next day's posts, and you will receive a Stripe receipt by email.</p>
<script>if(/[?&]paid=1/.test(location.search))document.getElementById('paid-note').hidden=false;</script>
<h1 class="page">Feature your business on EveryHour</h1>
<div class="post"><div class="body" style="border:0;padding-top:12px">
<p>EveryHour publishes a new post every hour about something people are talking about that day. For {e(price)}, your business can sponsor one of those posts.</p>
<h2 class="day" style="color:var(--ink)">What you get</h2>
<p>Your business name, a link to your website, and one sentence about what you do appear in a clearly labeled "Sponsored" box on one post. Each post has only one sponsor. The post stays on the site permanently, and it is included in the archive, the topic pages, the RSS feed and the sitemap.</p>
<p>Where it makes sense, I match your business to a post about a related topic. A coffee shop might appear on a morning post, and a gym on a post about fall routines.</p>
<p>You also get a link to the post that you can share with your own customers.</p>
<h2 class="day" style="color:var(--ink)">How it works</h2>
<p>At checkout, you enter your business name, your website and one sentence about your business. Payments received by 5 AM Pacific are placed in one of that day's posts. Payments received later are placed in the next day's posts.</p>
<p>Sponsor links are marked as sponsored, as search engines and advertising rules require. I review each business before it is published and will refund anything I cannot run, such as adult content, gambling, weapons or political campaigns.</p>
{cta}
</div></div>"""
    write("/sponsor/", page(f"Sponsor an hour | {CFG['title']}", f"Feature your business in an EveryHour post for {price}.", SITE + "/sponsor/", body, image="/og/sponsor.png"))

    # 404
    body = '<h1 class="page">That page is not here</h1><p class="pagedek">The link may be old or mistyped. The <a href="/">latest posts</a> and the <a href="/archive/">archive</a> are good places to start.</p>'
    (OUT / "404.html").write_text(page(f"Page not found | {CFG['title']}", CFG["description"], SITE + "/404.html", body, noindex=True))

    # sitemap
    urls = [(SITE + "/", posts[0]["dt"] if posts else now), (SITE + "/archive/", posts[0]["dt"] if posts else now), (SITE + "/about/", None), (SITE + "/stats/", None), (SITE + "/sponsor/", None)]
    urls += [(f"{SITE}/topics/{s}/", next(p["dt"] for p in posts if p["topic_slug"] == s)) for s, _ in topics]
    urls += [(p["url"], p["dt"]) for p in posts]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, d in urls:
        sm.append(f"<url><loc>{e(u)}</loc>" + (f"<lastmod>{d.astimezone(timezone.utc):%Y-%m-%dT%H:%M:%SZ}</lastmod>" if d else "") + "</url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")

    # rss
    items = []
    for p in posts[:50]:
        content = "".join(f"<p>{e(x)}</p>" for x in p["body"])
        items.append(f"""<item><title>{e(p['title'])}</title><link>{e(p['url'])}</link><guid isPermaLink="true">{e(p['url'])}</guid>
<pubDate>{format_datetime(p['dt'])}</pubDate><dc:creator>{e(AUTHOR)}</dc:creator><category>{e(p['topic'])}</category>
<description>{e(p['dek'])}</description><content:encoded><![CDATA[{content}]]></content:encoded></item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel><title>{e(CFG['title'])}</title><link>{SITE}/</link><description>{e(CFG['description'])}</description><language>en-us</language>
<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
<lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>
{''.join(items)}
</channel></rss>
"""
    (OUT / "feed.xml").write_text(rss)

    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    # IndexNow key file (Bing, Yandex, Seznam, Naver); see indexnow.py
    key = CFG.get("indexnow_key", "").strip()
    if key:
        (OUT / f"{key}.txt").write_text(key)

    # llms.txt: a plain summary for AI assistants and answer engines
    lines = [f"# {CFG['title']}", "", f"> {CFG['description']}", "",
             f"EveryHour publishes one short post every hour, Pacific time. Posts are written with AI and published by {AUTHOR}, "
             "who is responsible for the site. Posts list the sources their facts were checked against.", "",
             "## Pages", f"- [About and how posts are made]({SITE}/about/)", f"- [Archive]({SITE}/archive/)",
             f"- [RSS feed]({SITE}/feed.xml)", f"- [Sitemap]({SITE}/sitemap.xml)", "", "## Recent posts"]
    lines += [f"- [{p['title']}]({p['url']}): {p['dek']}" for p in posts[:48]]
    (OUT / "llms.txt").write_text("\n".join(lines) + "\n")
    print(f"Built {len(posts)} posts, {len(topics)} topics into {OUT}")
    return 0 if not errors else 0


if __name__ == "__main__":
    sys.exit(build())
