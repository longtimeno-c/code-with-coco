"""
quick test — verifies your token works and the api is reachable.
run this BEFORE the full pull. takes 5 seconds.

usage:
    1. copy .env.example to .env and fill in your values
    2. python3 test_token.py
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError


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


def main():
    load_env()
    ig_id = os.environ.get("IG_BUSINESS_ACCOUNT_ID", "").strip()
    token = os.environ.get("META_TOKEN", "").strip()

    if not ig_id or not token:
        print("ERROR: IG_BUSINESS_ACCOUNT_ID or META_TOKEN missing from .env")
        sys.exit(1)

    url = (
        f"https://graph.facebook.com/v19.0/{ig_id}"
        f"?fields=username,followers_count,media_count&access_token={token}"
    )

    try:
        with urlopen(Request(url), timeout=15) as r:
            data = json.loads(r.read())
        print("✓ token works!\n")
        print(f"  username:        @{data.get('username')}")
        print(f"  followers:       {data.get('followers_count'):,}")
        print(f"  total posts:     {data.get('media_count')}")
        print("\nyou're cleared to run: python3 pull_ig_analytics.py")
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"✗ http {e.code}: {body}")
        print("\nmost likely: token expired or wrong scope. regenerate via the meta dev console.")
        sys.exit(1)


if __name__ == "__main__":
    main()
