<div align="center">
<img src="../assets/readme_background.png" alt="code with coco" />
</div>

# <img src="../assets/instagram.png" height="48" style="vertical-align: middle;" /> &nbsp; content manager

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
