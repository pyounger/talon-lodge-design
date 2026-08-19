# UI Mapping — Daxa → Talon Lodge Platform

Pre-planning from Daxa's live demo (preview.hibootstrap.com/daxa-admin). Maps our
screens onto Daxa's existing pages/components so we build look/feel-first with minimal
from-scratch design, then wire the Laravel API behind it.

## Build rules (non-negotiable)
- **Use the theme framework — do not write custom CSS.** Style exclusively through Daxa's
  Sass theme variables and Angular Material's theming API (palettes, typography, density),
  plus Daxa's existing component classes/utilities. No bespoke stylesheets, no inline styles,
  no one-off overrides.
- Brand changes (Talon's colors/fonts) are made by **configuring the theme's Sass variables /
  Material theme**, in one place — never by adding CSS on individual pages.
- New screens are **composed from existing Daxa components**; if something's missing, build it
  from Daxa/Material primitives so it inherits the theme, rather than styling from scratch.
- `STYLE_GUIDE.md` therefore documents *which theme tokens and components to use*, not custom CSS.

## Daxa at a glance
- **Angular 20.1 + Angular Material 20.1** (purchased package v1.7.0; the demo advertises a
  newer build — we build against what's in the zip). Standalone components, SSR/SSG, Sass, TS.
- Theme tokens + framework details captured in [`STYLE_GUIDE.md`](../STYLE_GUIDE.md).
- **168+ pages, 254+ components, 45+ UI elements.** 5 dashboard variations (eCommerce, CRM,
  Project Management, LMS, Help Desk).
- Built-in: data tables, forms, file uploader, gallery, calendar, rich text editor,
  date/time picker, Google Maps, ApexCharts, Material Symbols/Icons, light/dark, RTL.
- **License: Regular $18** (end users not charged — correct for Talon's internal use).
  Extended $399 only if we ever resell the software.

## Observed design language (configure via the theme, don't reproduce in CSS)
- Light lavender/white canvas; **blue→purple gradient primary**; card surfaces with soft shadow.
- Left icon+label sidebar; sticky top bar with global search; Material Symbols iconography.
- Charts via ApexCharts. Light + dark themes.
- To rebrand for Talon: change the theme's **Sass palette variables / Angular Material theme**,
  not the pages. `STYLE_GUIDE.md` records the chosen token values.

## Screen mapping — reuse, don't rebuild

### Staff/admin
| Our screen | Daxa page/component to start from |
|---|---|
| Ops dashboard (gauges, fuel/oil-style KPIs, open issues) | **CRM / Project-Management dashboard** variation + stat tiles + ApexCharts |
| Lodges / Rooms / Activities (setup lists) | **Products Grid** + **Product Details**; Material tables + forms |
| Packages (list + rich editor) | **Products Grid / Details** + **Rich Text Editor** for description/details/fees |
| Inquiries / Reservation Requests / Brochure Requests | **Leads** (list) + **Tickets** (detail/status workflow) |
| Persons (golden record, detail) | **Contacts** / **Clients** / **Social Profile** (person 360 view) |
| Groups & Guest Lists | **Teams** / **Clients** (members of a group) |
| Trips (booking + members + events) | **Projects** + **Project Details** (a trip ≈ a dated project with members & events) |
| Merge Review Queue (Tier-3 dupes) | **Tickets/Leads** list with per-row Merge / Not-a-match actions |
| Boat / guide / room assignment by day | **Kanban Board** + **Calendar** + **Timeline** |
| On-property ops (breakfast, massage, activity schedules) | **Calendar** + **To Do List** + **Kanban** |
| Daily fish caught + weights | Material **Table** + form (custom log built on Daxa primitives) |
| Surveys + per-guest score | Forms + **ApexCharts** (score trend on the person 360 view) |
| Invoices / payments | **Invoices** + **Invoice Details** + **Pricing** |
| Staff users / roles | **Users** + **My Profile** |
| Settings (settings table UI) | Daxa settings/forms pages |

### Guest Portal (Viking-style guided flow)
| Portal pane | Daxa starting point |
|---|---|
| Home (hero, trip summary, completion checklist) | Profile/dashboard cards + progress widgets |
| Personal Info / Flight Info | Forms + **Date/Time Picker**; File Uploader for docs |
| Activities (scheduling grid, companion picker) | Table/Kanban + Material dialogs (companion picker is custom) |
| Adventures (browse + cart) | **Products Grid** + **Gallery** |
| Agenda | **Calendar** / **Timeline** |
| Cart & Payments | **Invoices** / **Pricing** (real Stripe wiring is a later phase) |

## Custom-built (Daxa has no direct equivalent — build from its primitives)
- Guest-matching / merge-and-undo UI (tables + dialogs + audit view).
- Activity companion picker with live min/max party enforcement.
- Per-day person→asset assignment grid (boats/guides/rooms).
- Fish-caught log and fish-processing instructions.
- Survey builder + per-guest survey score surface.

## Setup gotcha — pin dependency versions (important for the UI repo)
Daxa's zip ships **no `package-lock.json`**, and its `package.json` uses caret ranges
(`^20.1.7`). A plain `npm install` today resolves to newer patches (Angular 20.3.x,
ApexCharts 5.3.x) that Daxa's own demo code does **not** type-check against — you get ~90+
`ng serve` type errors (`document.querySelector` non-null, ApexCharts `chart.type` union,
`moment()` default-import), none of them our code. Fixes, for the developer scaffolding
`talon-lodge-ui`:
- Install the **exact** versions Daxa was built against (pin `package.json`, or use Daxa's
  intended lockfile / docs), rather than letting caret ranges float; **or**
- Commit a `package-lock.json` once a known-good install exists so builds are reproducible.
- `npm install` also needs `--legacy-peer-deps` (an Angular 20.x peer-range quirk).

(We confirmed this while trying to run it locally; the hosted demo builds fine because the
vendor built it before those patches shipped.)

## Next actions (when the licensed Daxa source is available in `references/daxa/`)
1. Read Daxa's theme config; record its Sass palette/typography variables in `STYLE_GUIDE.md`
   (values to set — not CSS to write). Adjust only the theme to rebrand for Talon.
2. Stand up the Angular shell (sidebar + topbar + routing) in `talon-lodge-ui`, stripped of
   demo pages, keeping Daxa's theme intact.
3. Build the look/feel-first screens per the mapping above **by composing existing Daxa/Material
   components** — no custom CSS. Lock as the blueprint.
4. Then wire each screen to the Laravel API.
