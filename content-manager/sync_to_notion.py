"""
instagram analytics → notion database sync.
pulls posts from ig graph api and pushes them directly to your notion database.

usage:
    1. copy .env.example to .env and fill in all values (including notion credentials)
    2. python3 sync_to_notion.py
    3. data appears in your notion database automatically

automation:
    - set up a cron job to run this daily at 3-4am PST
    - captures posts after they've had 24hrs to collect engagement
    - fresh analytics ready for you each morning
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError

API_VERSION = "v19.0"
IG_BASE = f"https://graph.facebook.com/{API_VERSION}"
NOTION_BASE = "https://api.notion.com/v1"
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


def get(url, headers=None):
    """http get with basic error handling. returns parsed json or None."""
    req = Request(url, headers=headers or {"User-Agent": "ig-analytics/1.0"})
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


def http_post(url, headers, data):
    """http post with json body. returns parsed json or None."""
    body_bytes = json.dumps(data).encode("utf-8")
    req = Request(url, data=body_bytes, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"  ! http {e.code}: {body[:500]}")
        return None
    except Exception as e:
        print(f"  ! request failed: {e}")
        return None


def fetch_media_list(ig_id, token, since_iso):
    """page through all media since `since_iso`. returns list of post dicts."""
    posts = []
    fields = "id,caption,media_type,media_product_type,timestamp,permalink,thumbnail_url"
    url = f"{IG_BASE}/{ig_id}/media?fields={fields}&limit=50&access_token={token}"
    page_count = 0
    while url:
        page_count += 1
        print(f"  fetching page {page_count} from instagram...")
        data = get(url)
        if not data or "data" not in data:
            break
        for post_data in data["data"]:
            post_dt = datetime.fromisoformat(post_data["timestamp"].replace("+0000", "+00:00"))
            if post_dt < since_iso:
                return posts
            posts.append(post_data)
        url = data.get("paging", {}).get("next")
        time.sleep(0.3)
    return posts


def fetch_post_insights(media_id, token):
    """fetch insights for a single post. fall back to a smaller metric set if the full one errors."""
    metrics_to_try = [POST_METRICS, "reach,saved,shares,likes,comments,total_interactions"]
    for metrics in metrics_to_try:
        url = f"{IG_BASE}/{media_id}/insights?metric={metrics}&access_token={token}"
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
            return 0
        return round(num / denom, 4)
    except Exception:
        return 0


def push_to_notion(database_id, notion_token, posts_data):
    """push posts to notion database. creates new pages for each post."""
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    print(f"\npushing {len(posts_data)} posts to notion...")
    success_count = 0

    for i, post in enumerate(posts_data, 1):
        print(f"  [{i}/{len(posts_data)}] pushing {post['media_id']}...")

        # format posted_at as notion date
        posted_dt = datetime.fromisoformat(post["posted_at"].replace("+0000", "+00:00"))

        # build notion page properties
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": post["caption_preview"][:100] or f"Post {post['media_id']}"
                        }
                    }
                ]
            },
            "Media ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": post["media_id"]
                        }
                    }
                ]
            },
            "Posted At": {
                "date": {
                    "start": posted_dt.isoformat()
                }
            },
            "Media Type": {
                "select": {
                    "name": post["media_type"]
                }
            },
            "Format": {
                "select": {
                    "name": post["format"]
                }
            },
            "Permalink": {
                "url": post["permalink"]
            },
            "Reach": {
                "number": post["reach"] if post["reach"] else 0
            },
            "Views": {
                "number": post["views"] if post["views"] else 0
            },
            "Likes": {
                "number": post["likes"] if post["likes"] else 0
            },
            "Comments": {
                "number": post["comments"] if post["comments"] else 0
            },
            "Saved": {
                "number": post["saved"] if post["saved"] else 0
            },
            "Shares": {
                "number": post["shares"] if post["shares"] else 0
            },
            "Total Interactions": {
                "number": post["total_interactions"] if post["total_interactions"] else 0
            },
            "Save Rate": {
                "number": post["save_rate"] if post["save_rate"] else 0
            },
            "Share Rate": {
                "number": post["share_rate"] if post["share_rate"] else 0
            }
        }

        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }

        result = http_post(f"{NOTION_BASE}/pages", headers, payload)
        if result and result.get("id"):
            success_count += 1
        else:
            print(f"    ! failed to push post {post['media_id']}")

        time.sleep(0.35)  # rate limit protection

    print(f"\n✓ successfully pushed {success_count}/{len(posts_data)} posts to notion")
    return success_count


def main():
    load_env()

    # instagram credentials
    ig_id = os.environ.get("IG_BUSINESS_ACCOUNT_ID", "").strip()
    meta_token = os.environ.get("META_TOKEN", "").strip()
    days_back = int(os.environ.get("DAYS_BACK", "90"))

    # notion credentials
    notion_token = os.environ.get("NOTION_TOKEN", "").strip()
    database_id = os.environ.get("NOTION_DATABASE_ID", "").strip()

    if not ig_id or not meta_token:
        print("ERROR: IG_BUSINESS_ACCOUNT_ID or META_TOKEN missing from .env")
        sys.exit(1)

    if not notion_token or not database_id:
        print("ERROR: NOTION_TOKEN or NOTION_DATABASE_ID missing from .env")
        print("  see README for how to set up notion integration")
        sys.exit(1)

    print(f"fetching last {days_back} days of posts from instagram...")
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    posts = fetch_media_list(ig_id, meta_token, cutoff)
    print(f"\nfound {len(posts)} posts in window. fetching insights...")

    posts_data = []
    for i, p in enumerate(posts, 1):
        print(f"  [{i}/{len(posts)}] {p['id']} ({p.get('media_product_type', 'unknown')})")
        insights = fetch_post_insights(p["id"], meta_token)
        caption = (p.get("caption") or "").replace("\n", " ").strip()
        reach = insights.get("reach", 0)
        posts_data.append({
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

    if not posts_data:
        print("no posts found in the time window. nothing to sync.")
        return

    # push to notion
    push_to_notion(database_id, notion_token, posts_data)


if __name__ == "__main__":
    main()
