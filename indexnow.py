"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver and others) about new pages.

Run after a deploy. Submits the home page, archive, feed and every post published in the
last LOOKBACK hours, so each hourly rebuild announces the post that just went live.
"""
import json, os, sys, urllib.request
from datetime import datetime, timedelta, timezone
import build

LOOKBACK = int(os.environ.get("INDEXNOW_LOOKBACK_HOURS", "3"))
key = build.CFG.get("indexnow_key", "").strip()
if not key:
    sys.exit("no indexnow_key in config.json; skipping")
posts, _ = build.load_posts()
cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK)
urls = [build.SITE + "/", build.SITE + "/archive/"] + [p["url"] for p in posts if p["dt"] >= cutoff]
payload = {"host": build.CFG["domain"], "key": key, "keyLocation": f"{build.SITE}/{key}.txt", "urlList": urls}
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(payload).encode(),
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow", r.status, len(urls), "urls")
except urllib.error.HTTPError as ex:  # 202 = accepted pending key check; 4xx should not fail the deploy
    print("IndexNow HTTP", ex.code, ex.read()[:200])
except urllib.error.URLError as ex:
    print("IndexNow unreachable:", ex.reason)
