"""
instagram graph api analytics pull.
fetches the last N days of posts from your ig business/creator account with per-post insights.
outputs a csv ready for spreadsheet or notion import.

usage:
    1. copy .env.example to .env and fill in your values
    2. python3 pull_ig_analytics.py
    3. csv lands in the same folder as posts_YYYY-MM-DD.csv

refresh notes:
    - meta long-lived tokens expire every 60 days
    - if a call returns "Invalid OAuth access token" → token expired, regenerate
"""

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError

API_VERSION = "v19.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"
POST_METRICS = "reach,saved,shares,likes,comments,total_interactions,views"


def load_env(path=".env"):
    """tiny .env parser — no dependencies."""
    if not os.path.exists(path):
        print(f"ERROR: no {path} file found.")
        print(f"  cp .env.example .env  → then fill in your values")
        sys.exit(1)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def get(url):
    """one http get with basic error handling. returns parsed json or None."""
    req = Request(url, headers={"User-Agent": "ig-analytics/1.0"})
    try:
        with urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"  ! http {e.code}: {body[:300]}")
        return None
    except Exception as e:
        print(f"  ! request failed: {e}")
        return None


def fetch_media_list(ig_id, token, since_iso):
    """page through all media since `since_iso`. returns list of post dicts."""
    posts = []
    fields = "id,caption,media_type,media_product_type,timestamp,permalink,thumbnail_url"
    url = f"{BASE}/{ig_id}/media?fields={fields}&limit=50&access_token={token}"
    page_count = 0
    while url:
        page_count += 1
        print(f"  fetching page {page_count}...")
        data = get(url)
        if not data or "data" not in data:
            break
        for post in data["data"]:
            post_dt = datetime.fromisoformat(post["timestamp"].replace("+0000", "+00:00"))
            if post_dt < since_iso:
                return posts
            posts.append(post)
        url = data.get("paging", {}).get("next")
        time.sleep(0.3)
    return posts


def fetch_post_insights(media_id, token):
    """fetch insights for a single post. fall back to a smaller metric set if the full one errors."""
    metrics_to_try = [POST_METRICS, "reach,saved,shares,likes,comments,total_interactions"]
    for metrics in metrics_to_try:
        url = f"{BASE}/{media_id}/insights?metric={metrics}&access_token={token}"
        data = get(url)
        if data and "data" in data:
            out = {}
            for m in data["data"]:
                name = m["name"]
                values = m.get("values", [])
                val = values[0].get("value", 0) if values else 0
                out[name] = val
            return out
    return {}


def safe_rate(num, denom):
    """ratio with safe div, rounded to 4dp."""
    try:
        if not denom:
            return ""
        return round(num / denom, 4)
    except Exception:
        return ""


def main():
    load_env()
    ig_id = os.environ.get("IG_BUSINESS_ACCOUNT_ID", "").strip()
    token = os.environ.get("META_TOKEN", "").strip()
    days_back = int(os.environ.get("DAYS_BACK", "90"))

    if not ig_id or not token:
        print("ERROR: IG_BUSINESS_ACCOUNT_ID or META_TOKEN missing from .env")
        sys.exit(1)

    print(f"pulling last {days_back} days of @{ig_id}...")
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    posts = fetch_media_list(ig_id, token, cutoff)
    print(f"\nfound {len(posts)} posts in window. fetching insights for each...")

    rows = []
    for i, p in enumerate(posts, 1):
        print(f"  [{i}/{len(posts)}] {p['id']} ({p.get('media_product_type', 'unknown')})")
        insights = fetch_post_insights(p["id"], token)
        caption = (p.get("caption") or "").replace("\n", " ").strip()
        reach = insights.get("reach", 0)
        rows.append({
            "media_id": p["id"],
            "posted_at": p["timestamp"],
            "media_type": p.get("media_type", ""),
            "format": p.get("media_product_type", ""),
            "permalink": p.get("permalink", ""),
            "caption_preview": caption[:200],
            "caption_length": len(caption),
            "reach": reach,
            "views": insights.get("views", ""),
            "likes": insights.get("likes", ""),
            "comments": insights.get("comments", ""),
            "saved": insights.get("saved", ""),
            "shares": insights.get("shares", ""),
            "total_interactions": insights.get("total_interactions", ""),
            "save_rate": safe_rate(insights.get("saved", 0), reach),
            "share_rate": safe_rate(insights.get("shares", 0), reach),
        })
        time.sleep(0.3)

    if not rows:
        print("no posts found in the time window. nothing to write.")
        return

    out_path = f"posts_{datetime.now().strftime('%Y-%m-%d')}.csv"
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\n✓ wrote {len(rows)} rows → {out_path}")


if __name__ == "__main__":
    main()
