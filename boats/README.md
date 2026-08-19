# Boat & crew photos for the Morning Display

Drop boat photos in this folder. The **Morning Display** (`docs/daily-display.html`) auto-loads
each boat's photo by its lowercased, hyphenated name:

| Boat | File to save here |
|------|-------------------|
| Raptor | `raptor.jpg` |
| Roamer | `roamer.jpg` |
| Retriever | `retriever.jpg` |
| Magnum | `magnum.jpg` |
| Pip | `pip.jpg` |
| Muktuk | `muktuk.jpg` |
| Raider | `raider.jpg` |

Notes
- **Landscape** photos work best (they fill the full slide behind a dark scrim). ~1600px wide is plenty.
- `.jpg` is expected; if you use `.png`, set the boat's `photo` field in Team instead (see below).
- If a photo is missing, that boat's slide falls back to the branded green gradient automatically.
- Captain portraits: set a `photo` (URL or path) on the captain record in Team; a circular portrait
  then shows on the boat slide (otherwise the captain's initials appear).

**Alternative (no files):** set a `photo` URL on a boat in `talon_team_v1` and it wins over the
`boats/<name>.jpg` convention — handy if the photos are hosted elsewhere.
