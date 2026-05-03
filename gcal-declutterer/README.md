<div align="center">
<img src="../assets/readme_background.png" alt="code with coco" />
</div>

# <img src="../assets/gcal.png" height="48" style="vertical-align: middle;" /> &nbsp; gcal declutterer

my google calendar was driving me crazy. nine calendars, all bright colors, all chaos. past events sat there cluttering up my week, so i wrote a tiny google apps script that runs every hour to finds events that already ended and make them gray. by wednesday your calendar is more gray than colorful, and somehow that makes the weekend feels so much closer!

## <img src="../assets/wrench.png" height="36" style="vertical-align: middle;" /> &nbsp; tutorial

### <img src="../assets/one.png" height="24" style="vertical-align: middle;" /> &nbsp; create gray calendar

1. go to [google calendar](https://calendar.google.com)
2. in the left sidebar, click the **+** next to "other calendars" → **create new calendar**
3. name it something like "past events" or "archive"
4. once it's created, click the three dots next to it → **settings** → set the color to gray, the hex i used was `#C1C1C1` 

### <img src="../assets/two.png" height="24" style="vertical-align: middle;" /> &nbsp; code setup

first, grab the calendar ids you'll need. for each calendar you want to clean up (including the archive one):
1. open that calendar's settings
2. scroll to **integrate calendar**
3. copy the **calendar id** — it looks like `xyz123@group.calendar.google.com`, or just your email for your primary calendar

then, set up the script in google apps script:
1. go to [script.google.com](https://script.google.com)
2. click **new project**
3. delete the default code and paste in [`gcal-declutter.gs`](./gcal-declutter.gs)
4. replace `REPLACE_WITH_GRAY_CALENDAR_ID` with your archive calendar's id
5. replace the entries in `CALENDAR_IDS` with the ids of the calendars you want to clean up from earlier
6. save (⌘S) and name your project

### <img src="../assets/three.png" height="24" style="vertical-align: middle;" /> &nbsp; set hourly trigger

1. in the apps script sidebar, click the clock icon (**triggers**)
2. click **add trigger** (bottom right)
3. set:
   - function: `movePastEventsToLightGrayCalendar`
   - event source: **time-driven**
   - type: **hour timer**
   - interval: **every hour**
4. save. google will ask for permissions, accept them

***that's it! you're done!!!!!!!!!!***

## <img src="../assets/star.png" height="36" style="vertical-align: middle;" /> &nbsp; episode
- tiktok: *coming soon*
- instagram: *coming soon*

## <img src="../assets/wink.png" height="36" style="vertical-align: middle;" /> &nbsp; kudos

feel free to copy, fork, and share. if you make a video with it, tag me! and if you remix the code in your own project, a quick credit in the file is appreciated.
- <img src="../assets/tiktok.png" height="20" style="vertical-align: middle;" /> &nbsp; [`@cocopuffffffffs`](https://tiktok.com/@cocopuffffffffs)
- <img src="../assets/instagram.png" height="20" style="vertical-align: middle;" /> &nbsp; [`@cocohdzz`](https://instagram.com/cocohdzz)