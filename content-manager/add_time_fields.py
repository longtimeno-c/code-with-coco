"""
add weekday and time posted fields to existing notion database.
these will be auto-populated by the sync script based on the posted_at timestamp.

usage:
    python3 add_time_fields.py
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


def add_time_fields(notion_token, database_id):
    """add weekday and time posted fields."""
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    new_properties = {
        "Weekday": {
            "select": {
                "options": [
                    {"name": "Monday", "color": "blue"},
                    {"name": "Tuesday", "color": "purple"},
                    {"name": "Wednesday", "color": "green"},
                    {"name": "Thursday", "color": "yellow"},
                    {"name": "Friday", "color": "orange"},
                    {"name": "Saturday", "color": "pink"},
                    {"name": "Sunday", "color": "red"}
                ]
            }
        },
        "Time Posted": {
            "rich_text": {}
        }
    }

    payload = {
        "properties": new_properties
    }

    print("adding weekday and time posted fields...")
    result = http_patch(f"{NOTION_BASE}/databases/{database_id}", headers, payload)

    if result and result.get("id"):
        print(f"\n✓ successfully added time fields!")
        print(f"\nnew fields:")
        print(f"  - Weekday (select) - auto-populated by sync script")
        print(f"  - Time Posted (text) - auto-populated by sync script (e.g., '3:45 PM')")
        print(f"\nthe sync script will now automatically fill these in based on your posted_at timestamp.")
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

    add_time_fields(notion_token, database_id)


if __name__ == "__main__":
    main()
