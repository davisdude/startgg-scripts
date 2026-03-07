# Start.gg Scripts

Miscellaneous scripts for interactive with start.gg. Previously lived in
[replay viewer].

## Scripts

### get\_startgg\_aliases

Given a user's slug (the `<slug>` bit of the URL
`https://www.start.gg/user/<slug>/` when you're on a user's profile), returns
a list of all gamer tags previously used for this account.

### ingest\_startgg

This script does a few things and should probably be split up. This assigns
VODs to start.gg sets based on a playlist or list of videos. It also outputs
a JSON of all the videos matched; intended for use with [iowa-melee-vods].

### merge\_json

Used to combine the output of [`ingest_startgg.py`](#ingest\_startgg) with
`replays.json` of [iowa-melee-vods]. It treats the video URL as the merge key.

### ingest

Parses a YouTube channel or playlist into a JSON file for use with
[iowa-melee-vods]. More error-prone and less featured than
[`ingest_startgg.py`](#ingest\_startgg), but far faster.


[replay-viewer]: https://github.com/davisdude/replay-viewer/tree/mine/scripts
[iowa-melee-vods]: https://github.com/davisdude/davisdude.github.io/tree/main/melee/iowa
