# magnusadventures.com

Static HTML for Firebase hosting. No WordPress, no build toolchain to install —
Python 3 and a browser are the whole dependency list.

This directory is separate from Island Ops and the reservation, package and
survey systems. Nothing here touches them.

## Building

    python3 build.py        # homepage          -> magnus-home.html
    python3 resort-pages.py # three resorts     -> magnus-resort-{castle,wailea,clayoquot}.html
    python3 make-dist.py    # deployable site   -> dist/

`build.py` reads `magnus-content.json` when it is present and falls back to the
literals at the top of the file when it is not. That JSON is what the control
panel exports, which is how an edit made in the panel reaches the page.

`make-dist.py` does the part the artifact preview hides: it wraps each page as a
real document with a doctype, a charset and — the one that matters — a viewport
tag. Without it a phone lays the page out at 980px. It also rewrites the preview
URLs to site paths, so `dist/` has no external links left in it.

Photographs are inlined as data URIs at build time, which is why the built pages
are large and the sources are not. The originals live in `img/`, `croatia/`,
`hvar/`, `elafiti/`, `food/` and `postranch/`.

## The control panel

`magnus-admin.html` edits the content and exports `magnus-content.json`. Six
tabs: Adventures, Resorts, Experiences, Food & Wine, Publications, Social wall.

The social wall will not publish a post until its rights field reads `granted`.
That is deliberate: the publish checkbox is disabled, not merely discouraged.
The panel also drafts the permission request to send the photographer.

## functions/

`instagram-hashtags.js` is a scheduled Firebase function that pulls hashtag
media daily and, once rights are granted, copies the image out of Instagram's
CDN into our own storage before the signed URL expires. It is written but not
deployed, and it needs real hashtags and a token first.

## Still open

- Social icons in the footer have no accounts wired to them.
- `Login` in the header is not wired.
- Fourteen adventure stories and four hashtags have cards but no pages yet;
  they render without anchors rather than as dead links.
- Scene copy on the four resort detail pages is written from public knowledge
  and wants checking against the properties.
