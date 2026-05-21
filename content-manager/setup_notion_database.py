"""
notion database setup for instagram analytics.
creates a new database with the correct schema for storing post analytics.

usage:
    1. make sure NOTION_TOKEN is in your .env file
    2. python3 setup_notion_database.py
    3. copy the database id that gets printed and add it to your .env file

this script will create a fresh database in your notion workspace with all the right columns.
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError

NOTION_BASE = "https://api.notion.com/v1"


def load_env(path=".env"):
    """tiny .env parser — no dependencies."""
    if not os.path.exists(path):
        print(f"ERROR: no {path} file found.")
        sys.exit(1)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def http_post(url, headers, data):
    """http post with json body."""
    body_bytes = json.dumps(data).encode("utf-8")
    req = Request(url, data=body_bytes, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"ERROR: http {e.code}")
        print(body)
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def http_get(url, headers):
    """http get with headers."""
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"ERROR: http {e.code}")
        print(body)
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def search_for_page(notion_token):
    """search for a page to use as parent. returns first page found."""
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # search for any page
    payload = {
        "filter": {
            "value": "page",
            "property": "object"
        },
        "page_size": 1
    }

    result = http_post(f"{NOTION_BASE}/search", headers, payload)
    if result and result.get("results"):
        return result["results"][0]["id"]
    return None


def create_database(notion_token, parent_page_id=None):
    """create a new notion database with instagram analytics schema."""
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # database schema
    parent_config = {
        "type": "page_id",
        "page_id": parent_page_id
    } if parent_page_id else {
        "type": "workspace",
        "workspace": True
    }

    payload = {
        "parent": parent_config,
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Instagram Analytics"
                }
            }
        ],
        "properties": {
            "Name": {
                "title": {}
            },
            "Media ID": {
                "rich_text": {}
            },
            "Posted At": {
                "date": {}
            },
            "Media Type": {
                "select": {
                    "options": [
                        {"name": "IMAGE", "color": "blue"},
                        {"name": "VIDEO", "color": "purple"},
                        {"name": "CAROUSEL_ALBUM", "color": "green"}
                    ]
                }
            },
            "Format": {
                "select": {
                    "options": [
                        {"name": "REELS", "color": "pink"},
                        {"name": "FEED", "color": "orange"},
                        {"name": "STORY", "color": "yellow"}
                    ]
                }
            },
            "Permalink": {
                "url": {}
            },
            "Reach": {
                "number": {
                    "format": "number"
                }
            },
            "Views": {
                "number": {
                    "format": "number"
                }
            },
            "Likes": {
                "number": {
                    "format": "number"
                }
            },
            "Comments": {
                "number": {
                    "format": "number"
                }
            },
            "Saved": {
                "number": {
                    "format": "number"
                }
            },
            "Shares": {
                "number": {
                    "format": "number"
                }
            },
            "Total Interactions": {
                "number": {
                    "format": "number"
                }
            },
            "Save Rate": {
                "number": {
                    "format": "percent"
                }
            },
            "Share Rate": {
                "number": {
                    "format": "percent"
                }
            }
        }
    }

    print("creating instagram analytics database in notion...")
    result = http_post(f"{NOTION_BASE}/databases", headers, payload)

    if result and result.get("id"):
        db_id = result["id"].replace("-", "")
        print(f"\n✓ database created successfully!")
        print(f"\ndatabase id: {db_id}")
        print(f"\nadd this to your .env file:")
        print(f"NOTION_DATABASE_ID={db_id}")
        print(f"\ndatabase url: https://notion.so/{db_id}")
        return db_id
    else:
        print("\n✗ failed to create database")
        return None


def main():
    load_env()
    notion_token = os.environ.get("NOTION_TOKEN", "").strip()

    if not notion_token:
        print("ERROR: NOTION_TOKEN missing from .env")
        sys.exit(1)

    # use the tracker page as parent
    parent_page_id = "3677b13f42d8812683d9d47f892bb81a"

    print(f"using tracker page as parent: {parent_page_id}")
    print("creating database...\n")

    create_database(notion_token, parent_page_id)


if __name__ == "__main__":
    main()
