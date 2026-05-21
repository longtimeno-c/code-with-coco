"""
add custom tracking fields to existing notion database.
adds fields for analyzing content strategy: hook type, style, lighting, time category, etc.

usage:
    python3 add_tracking_fields.py

this updates your existing instagram analytics database with new properties for manual tracking.
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


def http_patch(url, headers, data):
    """http patch with json body."""
    body_bytes = json.dumps(data).encode("utf-8")
    req = Request(url, data=body_bytes, headers=headers, method="PATCH")
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


def add_tracking_fields(notion_token, database_id):
    """add custom tracking fields to existing database."""
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # new properties for content strategy analysis
    new_properties = {
        "Hook Type": {
            "rich_text": {}
        },
        "Style": {
            "select": {
                "options": [
                    {"name": "Talking Head", "color": "blue"},
                    {"name": "B-Roll", "color": "purple"},
                    {"name": "Text Overlay", "color": "green"},
                    {"name": "Tutorial", "color": "yellow"},
                    {"name": "POV", "color": "orange"},
                    {"name": "Voiceover", "color": "pink"},
                    {"name": "Mixed", "color": "gray"}
                ]
            }
        },
        "Lighting": {
            "select": {
                "options": [
                    {"name": "Natural", "color": "green"},
                    {"name": "Ring Light", "color": "blue"},
                    {"name": "Studio", "color": "purple"},
                    {"name": "Mixed", "color": "gray"}
                ]
            }
        },
        "Time Category": {
            "select": {
                "options": [
                    {"name": "Morning (6am-12pm)", "color": "yellow"},
                    {"name": "Afternoon (12pm-5pm)", "color": "orange"},
                    {"name": "Evening (5pm-10pm)", "color": "blue"},
                    {"name": "Night (10pm-6am)", "color": "purple"}
                ]
            }
        },
        "Content Topic": {
            "multi_select": {
                "options": [
                    {"name": "Tech", "color": "blue"},
                    {"name": "Stanford", "color": "red"},
                    {"name": "Coding", "color": "green"},
                    {"name": "Life", "color": "pink"},
                    {"name": "Tutorial", "color": "purple"},
                    {"name": "Behind the Scenes", "color": "gray"}
                ]
            }
        },
        "Notes": {
            "rich_text": {}
        }
    }

    payload = {
        "properties": new_properties
    }

    print("adding custom tracking fields to database...")
    result = http_patch(f"{NOTION_BASE}/databases/{database_id}", headers, payload)

    if result and result.get("id"):
        print(f"\n✓ successfully added tracking fields!")
        print(f"\nnew fields:")
        print(f"  - Hook Type (text) - describe your hook (e.g., 'question', 'POV', 'statement')")
        print(f"  - Style (select) - video style")
        print(f"  - Lighting (select) - lighting setup")
        print(f"  - Time Category (select) - when you posted")
        print(f"  - Content Topic (multi-select) - tag your topics")
        print(f"  - Notes (text) - any observations")
        print(f"\nthese are all optional fields you can manually fill in notion.")
        print(f"use them to track what works and identify patterns!")
        return True
    else:
        print("\n✗ failed to add fields")
        return False


def main():
    load_env()
    notion_token = os.environ.get("NOTION_TOKEN", "").strip()
    database_id = os.environ.get("NOTION_DATABASE_ID", "").strip()

    if not notion_token or not database_id:
        print("ERROR: NOTION_TOKEN or NOTION_DATABASE_ID missing from .env")
        sys.exit(1)

    add_tracking_fields(notion_token, database_id)


if __name__ == "__main__":
    main()
