# _build — prototype sources

The `.html` prototypes in the repo root are **assembled outputs** — self-contained
(brand mark + data inlined) and directly editable. This folder holds the **sources**
used to generate them, so the prototypes can be rebuilt or reworked from git alone.

## What's here
- **`*.template.html`** — the editable source for each prototype, with `__EAGLE__` /
  `__DATA__` / `__MASTHEAD__` placeholders. Examples:
  - `rescal.template.html` → `reservation-calendar.html`
  - `styleguide.template.html` → `style-guide.html`
  - `survey-dashboard.template.html` → `survey-dashboard.html`
  - `survey-guest.template.html` → `survey-guest.html`
  - `review.template.html`, `manual.template.html` → project-review / system-overview
- **`assemble-*.js`** — inject the placeholders and wrap into the standalone HTML.
- **`extract-cal.js` / `extract2.js` / `extract-final.js`** — parse the 2027 reservation
  XLSX into `reservation-2027.json` (the calendar's data).
- **`wrap-*.js`, `build-shared-demo.js`, `snap-photos.js`, `inject-home.js`,
  `mkuri.js`, `mkico.js`, `colors.js`** — one-off helpers (report wrapping, the shared
  demo, portal snapshot photos, data-URI + favicon generation, colour audits).
- **Data:** `reservation-2027.json` (calendar data), `survey.txt` / `survey_raw.txt`
  (extracted survey questions/results), `eagle-datauri.txt` (the eagle mark as a data URI).
- **Standalone artifact sources:** `portal-home-snapshot.html`, `portal-profile-sample.html`,
  `palette-compare.html`.

## ⚠ Paths
The `assemble-*.js` / `*.js` scripts contain **hard-coded absolute paths** from the
original machine (a Windows scratchpad). On a fresh clone or a different machine, update
the two path constants at the top of each script (a source dir and the repo dir) before
running. The logic is otherwise portable Node — no dependencies.

## Not committed (regenerate as needed)
- The eagle PNG source lives at `brand/logo/talon-eagle-mark.png` (regenerate
  `eagle-datauri.txt` from it if needed).
- The masthead data URI is derived from `talon-app2026-ui/public/portal-masthead.jpg`.
- The reservation XLSX is Phil's file (re-provide to re-extract).
