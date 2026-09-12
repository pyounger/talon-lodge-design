# UI Mapping — Talon Lodge Platform

Maps our screens onto the framework each surface is built in. **Two surfaces, two front-end
approaches:**

- **Staff / admin — Daxa** (Angular 20.1 + Angular Material), themed, no custom CSS.
  Pre-planned from Daxa's live demo (preview.hibootstrap.com/daxa-admin) so we build
  look/feel-first with minimal from-scratch design, then wire the Laravel API behind it.
- **Guest portal — Tailwind.** Andy's decision, for greater flexibility and design control on
  the one surface guests actually see. Applies to the guest portal *only*.

Both surfaces take their brand values from the same token set, `brand/_talon-tokens.scss`.

## Build rules (non-negotiable)

### Shared — the brand tokens are the contract
- `brand/_talon-tokens.scss` (the `--talon-*` custom properties) is the **single source of truth
  for color, typography and spacing on both surfaces.** Daxa's Sass palette and Tailwind's theme
  config both read *from* these tokens.
- A brand change is made **once, in the tokens** — never separately in each surface.
- Two styling systems drifting apart on color and type is the main risk the split introduces.
  The token discipline above is what prevents it; treat a hard-coded color in either surface as
  a defect.
- `STYLE_GUIDE.md` documents *which tokens and components to use*, not custom CSS.

### Staff / admin — Daxa + Angular Material
- **Use the theme framework — do not write custom CSS.** Style exclusively through Daxa's
  Sass theme variables and Angular Material's theming API (palettes, typography, density),
  plus Daxa's existing component classes/utilities. No bespoke stylesheets, no inline styles,
  no one-off overrides.
- Brand changes (Talon's colors/fonts) are made by **configuring the theme's Sass variables /
  Material theme**, in one place — never by adding CSS on individual pages.
- New screens are **composed from existing Daxa components**; if something's missing, build it
  from Daxa/Material primitives so it inherits the theme, rather than styling from scratch.

### Guest portal — Tailwind
- The portal is built in **Tailwind**, not Daxa. This is a deliberate, scoped exception to the
  rule above: it covers the guest portal only, and staff/admin screens stay on Daxa.
- Tailwind's theme config must be **driven by `brand/_talon-tokens.scss`**, not Tailwind's
  default palette, so the portal and the admin screens remain one visual system.
- The prototype `guest-portal.html` stays the reference for portal behavior and layout.

## Daxa at a glance (the staff/admin stack)
- **Angular 20.1 + Angular Material 20.1** (purchased package v1.7.0; the demo advertises a
  newer build — we build against what's in the zip). Standalone components, SSR/SSG, Sass, TS.
- Theme tokens + framework details captured in [`STYLE_GUIDE.md`](../STYLE_GUIDE.md).
- **168+ pages, 254+ components, 45+ UI elements.** 5 dashboard variations (eCommerce, CRM,
  Project Management, LMS, Help Desk).
- Built-in: data tables, forms, file uploader, gallery, calendar, rich text editor,
  date/time picker, Google Maps, ApexCharts, Material Symbols/Icons, light/dark, RTL.
- **License: Regular $18** (end users not charged — correct for Talon's internal use).
  Extended $399 only if we ever resell the software.

## Observed design language — staff/admin (configure via the theme, don't reproduce in CSS)
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

### Guest Portal (Viking-style guided flow) — **Tailwind, not Daxa**
Built in Tailwind per the build rules above. The patterns below say what each pane *is* — they
are framework-agnostic descriptions, not Daxa component names.

| Portal pane | Pattern |
|---|---|
| Home (hero, trip summary, completion checklist) | Profile/dashboard cards + progress widgets |
| Personal Info / Flight Info | Forms + date/time picker; file uploader for docs |
| Activities (scheduling grid, companion picker) | Table/board + dialogs (companion picker is custom) |
| Adventures (browse + cart) | Product grid + gallery |
| Agenda | Calendar / timeline |
| Cart & Payments | Invoice / pricing layout (real Stripe wiring is a later phase) |

## Custom-built (no direct equivalent in either framework — build from primitives)
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

## Next actions

### Staff / admin (when the licensed Daxa source is available in `references/daxa/`)
1. Read Daxa's theme config; record its Sass palette/typography variables in `STYLE_GUIDE.md`
   (values to set — not CSS to write). Adjust only the theme to rebrand for Talon.
2. Stand up the Angular shell (sidebar + topbar + routing) in `talon-lodge-ui`, stripped of
   demo pages, keeping Daxa's theme intact.
3. Build the look/feel-first screens per the mapping above **by composing existing Daxa/Material
   components** — no custom CSS. Lock as the blueprint.
4. Then wire each screen to the Laravel API.

### Guest portal
1. Confirm Tailwind's theme config reads from `brand/_talon-tokens.scss` rather than Tailwind's
   default palette — this is what keeps the two surfaces in one visual system.
2. Portal shell (nav, header, layout), then the first screens wired to the scoped API endpoints.
