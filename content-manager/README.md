<div align="center">
<img src="../assets/readme_background.png" alt="code with coco" />
</div>

# <img src="../assets/improvement.svg" height="48" style="vertical-align: middle;" /> &nbsp; content manager

ever wish you could just download your instagram analytics into a spreadsheet? every "analytics tool" wants $30/month to show you numbers meta already has. so i built a tiny python script that pulls your own data directly from the instagram graph api and spits out a csv. no third-party tools, no monthly fees, just your data.

## <img src="../assets/info.png" height="36" style="vertical-align: middle;" /> &nbsp; what it does

reads the last 90 days of your instagram posts and pulls per-post insights — reach, views, saves, shares, likes, comments. outputs a csv you can import into notion, google sheets, or whatever you want.

includes two derived metrics: `save_rate` and `share_rate` (saves/shares divided by reach). these matter more than raw views — they tell you what people actually wanted to keep or send.

## <img src="../assets/wrench.png" height="36" style="vertical-align: middle;" /> &nbsp; tutorial

### <img src="../assets/one.png" height="24" style="vertical-align: middle;" /> &nbsp; get your ig business account id + long-lived token

you need an instagram business or creator account (personal accounts can't use the api), a facebook page linked to your ig, and a meta developer app.

if you already have your account id and token from another project, skip to step 2. otherwise:

1. go to [developers.facebook.com](https://developers.facebook.com) → create a new app → use case: "other" → type: "business"
2. add the instagram graph api product
3. open graph api explorer (under tools)
4. select your app → generate access token → grant these permissions:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_show_list`
   - `pages_read_engagement`
5. find your ig business account id by running this in the api explorer:
   ```
   GET /me/accounts?fields=name,instagram_business_account
   ```
6. exchange your short-lived token for a long-lived one (60 day expiry):
   ```
   GET /oauth/access_token?
     grant_type=fb_exchange_token
     &client_id=YOUR_APP_ID
     &client_secret=YOUR_APP_SECRET
     &fb_exchange_token=YOUR_SHORT_TOKEN
   ```

save both values somewhere safe. **not in this repo.**

### <img src="../assets/two.png" height="24" style="vertical-align: middle;" /> &nbsp; clone and configure

```bash
git clone https://github.com/cocohernandez/code-with-coco.git
cd code-with-coco/content-manager
cp .env.example .env
```

open `.env` in your editor, paste in your ig business account id + long-lived token. `.env` is gitignored so it won't be committed.

### <img src="../assets/three.png" height="24" style="vertical-align: middle;" /> &nbsp; run the scripts

```bash
python3 test_token.py        # 5-second sanity check
python3 pull_ig_analytics.py # full pull
```

the first script verifies your token works. the second one pulls all your data and outputs `posts_YYYY-MM-DD.csv`.

*that's it! you're done!!!!!!!!!!*

## <img src="../assets/sync.png" height="36" style="vertical-align: middle;" /> &nbsp; notion sync (optional)

want your analytics automatically pushed to notion every day? here's how:

### <img src="../assets/one.png" height="24" style="vertical-align: middle;" /> &nbsp; create notion integration

1. go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. click "new integration"
3. name it (e.g., "instagram analytics")
4. copy the integration token (starts with `secret_` or `ntn_`)
5. add to your `.env`:
   ```bash
   NOTION_TOKEN=your_token_here
   ```

### <img src="../assets/two.png" height="24" style="vertical-align: middle;" /> &nbsp; set up database

```bash
python3 setup_notion_database.py
```

this creates a fresh notion database with all the right columns. copy the database id it prints and add it to your `.env`:

```bash
NOTION_DATABASE_ID=your_database_id_here
```

### <img src="../assets/three.png" height="24" style="vertical-align: middle;" /> &nbsp; test the sync

```bash
python3 sync_to_notion.py
```

this pulls your instagram data and pushes it directly to notion. check your notion database to see all your posts with full analytics.

### <img src="../assets/four.png" height="24" style="vertical-align: middle;" /> &nbsp; automate daily sync (optional)

the cron job is already set up to run at 3:30 AM PST every day! it syncs your posts after they've had 24 hours to collect engagement, so you wake up to fresh analytics each morning.

check the logs: `tail -f sync.log`

to disable: `crontab -e` and comment out or delete the instagram analytics line.

## <img src="../assets/chart.png" height="36" style="vertical-align: middle;" /> &nbsp; what's in the csv

| column | what it is |
|---|---|
| `media_id` | unique post id |
| `posted_at` | iso timestamp |
| `media_type` | image / video / carousel |
| `format` | feed / reels / story |
| `permalink` | direct link |
| `caption_preview` | first 200 chars |
| `caption_length` | full char count |
| `reach` | unique accounts that saw it |
| `views` | total plays (reels only) |
| `likes`, `comments`, `saved`, `shares` | the standard stuff |
| `total_interactions` | sum of all engagement |
| `save_rate` | saved / reach |
| `share_rate` | shares / reach |

## <img src="../assets/test.png" height="36" style="vertical-align: middle;" /> &nbsp; content strategy tracking

if you're using notion sync, your database includes optional tracking fields to help you figure out what works. manually fill these in for each post to identify patterns:

**tracking fields:**
- **hook type** (text) - how you opened ("question", "POV", "bold statement", "tutorial intro", etc.)
- **style** (select) - video style (talking head, b-roll, text overlay, tutorial, POV, voiceover, mixed)
- **lighting** (select) - lighting setup (natural, ring light, studio, mixed)
- **time category** (select) - when you posted (morning, afternoon, evening, night)
- **content topic** (multi-select) - tag your topics (tech, stanford, coding, life, tutorial, behind the scenes)
- **notes** (text) - anything you noticed while filming or posting

**how to use this:**

after a few weeks of tracking, filter and sort your notion database to find patterns:
- which hooks get the highest save rate?
- does lighting affect engagement?
- what time category performs best for your audience?
- which topics drive the most shares?

sort by `save_rate` or `share_rate` descending, then look for commonalities in your top performers. this is how you build a data-driven content strategy instead of guessing.

## <img src="../assets/clock.png" height="36" style="vertical-align: middle;" /> &nbsp; token refresh

meta long-lived tokens expire every 60 days. set a calendar reminder. when it's about to expire, repeat step 6 from the tutorial with your current token (before it dies) to get a fresh 60 days.

## <img src="../assets/lock.png" height="36" style="vertical-align: middle;" /> &nbsp; security

- never commit your `.env` file
- never paste your token anywhere public (github, discord, screenshots)
- if you accidentally leak it, revoke immediately at [developers.facebook.com](https://developers.facebook.com) → your app → app review → revoke token, then regenerate

## <img src="../assets/star.png" height="36" style="vertical-align: middle;" /> &nbsp; episode
- coming soon!

## <img src="../assets/wink.png" height="36" style="vertical-align: middle;" /> &nbsp; kudos

feel free to copy, fork, and share. if you make a video with it, tag me! and if you remix the code in your own project, a quick credit in the file is appreciated.
- <img src="../assets/tiktok.png" height="20" style="vertical-align: middle;" /> &nbsp; [`@cocopuffffffffs`](https://tiktok.com/@cocopuffffffffs)
- <img src="../assets/instagram.png" height="20" style="vertical-align: middle;" /> &nbsp; [`@cocohdzz`](https://instagram.com/cocohdzz)
