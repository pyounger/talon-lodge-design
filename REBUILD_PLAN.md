# talonlodge.com — Rebuild Plan

Rebuild the public marketing site on a modern stack, **keeping the existing
design**, with a new control panel replacing the 2011-era CMS.

Scope decided with Phil, 2026-09-14:

- **Website CMS only.** The 37 `manage_*.php` lodge-operations screens are a
  separate project and are not touched here.
- **Standalone.** Its own codebase and deploy, not folded into
  `talon-lodge-api` / `talon-app2026-*`. The enquiry form posts to the
  platform's `inquiries` endpoint per `INQUIRY_INTAKE.md`.
- **Modern hosting.** Off the cPanel/PHP 5.4 box.

This proposes; nothing here is built yet.

---

## 1. What exists today

The current site is a custom PHP MVC framework ("CPF") with Smarty templates
and the Outlet ORM, running on PHP 5.4. Its admin is 24 backend controllers
over 28 database tables.

**Public routes** (`app/config/routes.php` plus the main navigation): 25 content
pages — `/about/`, `/our-story/`, `/location/`, `/people/`, `/difference/`,
`/talon-service/`, `/alaska-adventure/`, `/lodge-accommodations/`, `/fishing/`,
`/sport-fishing/`, `/freshwater-fishing/`, `/fishing-calendar/`, `/rates/`,
`/spa/`, `/treatment-menu/`,
`/alaskas-only-open-air-massage-pavilion/`, `/cuisine-events/`,
`/chef-series/`, `/winemaker-series/`, `/guides-and-gear/`, `/faq/`,
`/contacts/`, `/brochure/`, `/gallery/`, `/recipe-finder/` — plus
`/reservation/`, a WordPress blog at `/blog/`, `/sitemap.xml`, and a catch-all
slug route serving CMS pages.

---

## 2. Content model

Derived from the 28 live tables and the 24 admin controllers. Grouped into what
the new control panel actually needs to manage.

| Collection | Replaces | Notes |
|---|---|---|
| **Pages** | `pages`, `blocks`, `layouts`, `layout_elements`, `template_layout` | The current page builder is five tables deep. A block-based editor collapses this to one collection with a blocks field. |
| **Navigation** | `navigation_menus`, `navigation_menu_elements` | Main, footer and mobile menus. |
| **Media** | `photos`, `videos` | One library. Derivatives generated on upload — see §4. |
| **Galleries** | `galleries`, `gallery_types` | Ordered sets of media with a type/category. |
| **Packages & Rates** | `packages` | Feeds `/rates/`. Check against the platform's package model before finalising — this is the one collection that may want to read from the API rather than own its data. |
| **Reviews** | `reviews` | Testimonials surfaced site-wide. |
| **Recipes** | `recipes`, `recipe_categories`, `recipes_in_categories` | Powers `/recipe-finder/`. Confirm this is still wanted — see §7. |
| **Banners** | `banners`, `banners_visits` | Promo slots. Visit counting is analytics, not CMS; drop it. |
| **Users & Roles** | `users`, `usergroups`, `usertokens`, `sys_rights`, `sys_securables`, `sys_controllers` | Six tables of bespoke ACL replaced by the CMS's own roles. |
| **Email templates** | `email_templates` | Only if the site still sends mail directly; the platform may own this. |

**Not carried over:** `facebook`, `facebook_tokens`, `twitter` (social-feed
integrations, long dead), `cities`/`states` (lookup data with one live
consumer), `messages` (enquiries now go to the platform).

That is **28 tables down to roughly 9 collections**.

---

## 3. Keeping the design

The brief is to preserve the design, so the rebuild starts from the live site's
own values, extracted from `static/css/frontend/`:

| Role | Value | Uses |
|---|---|---|
| Primary text / dark ground | `#332a1f` warm brown | 35 |
| Brand teal | `#1f4c59` | 30 |
| White | `#ffffff` | 24 |
| Accent rust | `#a93102` | 18 |
| Gold / amber | `#e0a213` | 4 |
| Pale cream | `#ede8c4` | 2 |

Typography is Times / Times New Roman for display and body, with a licensed
webfont **BalticaPlain** (and **BalticaItalic**) used across headings, plus
Arial for UI text.

> **Discrepancy worth settling first.** `brand/_talon-tokens.scss` in this repo
> defines a different palette — `#0e7c6f` teal, `#bd5836` salmon, `#a9791f`
> gold. Those tokens are for the **internal platform**, not the public site.
> They are the same family but distinctly different values. If the rebuilt site
> should adopt the platform's palette, that is a redesign, not a rebuild, and
> changes this brief. Assumption until told otherwise: **match the live site.**

Two things to confirm before build: whether the **Baltica** font licence covers
continued web use, and whether we have the original files (`brand/fonts/` is
currently empty).

---

## 4. Recommended stack

**Next.js (App Router) + Payload CMS + PostgreSQL.**

Payload runs *inside* the Next.js app, so the site and its control panel are one
codebase and one deploy. The reasons it fits this brief specifically:

- **Images are the whole problem.** The audit found the current site's headline
  fault is `JPEG_QUALITY = 100` producing 367 KB average for 799×495 photos.
  Payload's media library generates sized derivatives on upload and Next's image
  pipeline serves AVIF/WebP automatically. The failure mode that caused this
  cannot recur — there is no hand-rolled resize code to misconfigure.
- **The control panel is first-class**, not something to build from scratch.
  Non-technical staff get drafts, preview, version history and a real media
  library out of the box.
- **Zero jQuery.** The current bundle is 453 KB of 2011-era JavaScript, 46% of
  it a jQuery UI build used for one datepicker.
- **Self-hostable** on any VPS via Docker, or Vercel.

### The one real fork

Payload is TypeScript/Node. Your existing people are PHP-oriented — Andy
deploys by FTP, and `talon-lodge-api` is Laravel. The PHP-native alternative is
**Laravel + Filament**, which would sit closer to the platform and to the skills
already in the building.

Honest read: Payload gives the better site, Laravel gives the better team
continuity. The deciding question is **who maintains this in two years.** If the
answer is the same people who maintain `talon-lodge-api`, take Laravel +
Filament and accept doing more image work by hand. If it is going to be
contracted out or is mostly hands-off, take Payload.

This needs a decision before any code is written.

---

## 5. Migration

**Content.** The live database is the source. The only dumps in the repo are
from 2014 and 2015 (`_dump/`), which are useful for reading the schema and
useless as content. A current dump is needed.

**Images.** ~2,600 files in `uploads/photos/frontend/`, of which 575 are
`-orig` masters with the rest derivatives. **Migrate the masters only** and let
the new pipeline regenerate everything else — that discards the oversized
derivatives rather than carrying them across, and is why the 166 MB problem does
not follow us.

**URLs.** Every existing path must keep working. The 25 nav routes plus the
catch-all slug route map to 301s in the new app. Getting this wrong costs
search rankings, so it needs a redirect map checked against real traffic data
before launch — not guessed from the menu.

**The blog.** WordPress at `/blog/` is a separate install. Decide: migrate posts
into the new CMS, leave it where it is, or retire it.

---

## 6. Phases

1. **Decide the stack** (§4) and settle the palette question (§3).
2. **Foundation** — repo, content model, deploy pipeline, a page rendering from
   the CMS.
3. **Design system** — the live site's palette and type as tokens, components
   built from them, checked side by side against production.
4. **Templates** — the page types: standard content, gallery, rates, recipe
   finder, contact.
5. **Content migration** — masters and content from the live database, with the
   redirect map.
6. **Enquiry integration** — post to the platform per `INQUIRY_INTAKE.md`.
7. **Launch** — staging, redirect verification, cutover.

Phases 2–4 are where the bulk of the work sits.

---

## 7. Open questions

1. **Stack** — Payload or Laravel + Filament (§4). Blocks everything.
2. **Palette** — live site values, or the platform's tokens (§3).
3. **Baltica font licence** — do we have the files and the right to keep using
   them on the web?
4. **Recipe finder** — 3 tables and a route for a feature that may no longer
   earn its place. Keep or retire?
5. **Rates/packages** — does the site own this content, or read it from the
   platform so rates are maintained once?
6. **The blog** — migrate, leave, or retire (§5).
7. **Reservation flow** — `/reservation/` is currently a booking journey in the
   legacy app. Does the rebuilt site keep it, or hand off to the platform?

---

## Related

- `WEBSITE_PERFORMANCE_AUDIT.md` — what is wrong with the current site, measured.
  Still the best statement of what the rebuild must not repeat.
- `DEPLOY_STAGE_1_2.md` — the interim fixes already made to the live site.
- `INQUIRY_INTAKE.md` — the enquiry contract the rebuilt form must satisfy.
