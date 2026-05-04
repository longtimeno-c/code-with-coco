"""
code with coco ep 3 ✿ who doesn't follow me back?
~ pure stdlib, just point it at your meta data export ~
"""

import json
from pathlib import Path

# ─── colors (pink/purple bc obvi) ────────────────────────────
PINK = "\033[38;5;213m"
PURPLE = "\033[38;5;141m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_usernames(path: Path, key: str | None = None) -> set[str]:
    """meta wraps usernames in: {string_list_data: [{value: 'username'}]}"""
    data = json.loads(path.read_text())
    entries = data[key] if key else data  # following is dict-wrapped, followers isn't
    return {e["string_list_data"][0]["value"] for e in entries}


def main():
    # ─── point this at your unzipped meta export ─────────────
    base = Path("instagram-data/connections/followers_and_following")

    followers = load_usernames(base / "followers_1.json")
    following = load_usernames(base / "following.json", key="relationships_following")

    not_following_back = following - followers   # i follow them, they don't follow me
    fans = followers - following                 # they follow me, i don't follow them
    mutuals = followers & following

    # ─── pretty print ────────────────────────────────────────
    print(f"\n{PINK}{BOLD}✿ instagram audit ✿{RESET}\n")
    print(f"  {DIM}followers:{RESET} {len(followers)}")
    print(f"  {DIM}following:{RESET} {len(following)}")
    print(f"  {DIM}mutuals:  {RESET} {len(mutuals)}\n")

    print(f"{PURPLE}{BOLD}↓ doesn't follow you back ({len(not_following_back)}){RESET}")
    for user in sorted(not_following_back):
        print(f"  {PINK}·{RESET} {user}")

    print(f"\n{PURPLE}{BOLD}↓ you don't follow back ({len(fans)}){RESET}")
    for user in sorted(fans):
        print(f"  {PINK}·{RESET} {user}")

    # ─── save to file (optional but nice) ────────────────────
    Path("audit_results.txt").write_text(
        "doesn't follow you back:\n" + "\n".join(sorted(not_following_back)) +
        "\n\nyou don't follow back:\n" + "\n".join(sorted(fans))
    )
    print(f"\n{DIM}saved to audit_results.txt ✓{RESET}\n")


if __name__ == "__main__":
    main()