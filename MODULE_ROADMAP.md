# Module Roadmap — Talon Lodge Platform

Every module from the [module map](module-map.html) keyed to a build phase, dependency, and
status. This is a **living document**: when the system changes, this file and
[`module-map.html`](module-map.html) are updated in the same change so the docs and the system
always match. Lifecycle phases here mirror the module map; build order front-loads the
foundations everything else depends on.

**Status:** ✅ done · 🟡 in progress · ⬜ not started
**Cross-refs:** [ROADMAP.md](../ROADMAP.md) (narrative) · [DATABASE_DESIGN.md](DATABASE_DESIGN.md) · [UI_MAPPING.md](UI_MAPPING.md)

---

## Phase 0 — Foundations (platform + the data hub)
Nothing in the lifecycle works until these exist. Built first.

| Module | Status | Notes |
|---|---|---|
| Data model — Person / Group / Trip / Profile / Assignment | 🟡 | Designed in DATABASE_DESIGN.md; not yet Laravel/MySQL migrations |
| DB schema (Phase-1 tables) | 🟡 | Postgres draft in `db/migrations`; to re-express as Laravel migrations on **Aurora MySQL** |
| Seed data (49 packages + lookups) | 🟡 | Extracted to `db/seed/seed.sql` (Postgres); to become a Laravel seeder |
| Auth — staff roles + guest magic-link | ⬜ | |
| Multi-site tenancy | ⬜ | Talon, Bluff House, Alaska Luxury, Magnus |
| Object storage (photos/videos/licenses) | ⬜ | S3, presigned URLs |
| Settings table | ⬜ | Config in-app, not config files |
| API scaffold (Laravel) | ⬜ | Awaiting `talon-lodge-api` repo |
| UI shell (Angular + Daxa) | ⬜ | Theme captured in STYLE_GUIDE.md; awaiting `talon-lodge-ui` repo |

## Phase 1 — Setup & Inventory
| Module | Status | Depends on |
|---|---|---|
| Package Management | ⬜ | Phase 0 |
| Rooms Management | ⬜ | Phase 0 |
| Boats & Activities Management | ⬜ | Phase 0 |
| Captains & Guides Management | ⬜ | Phase 0 |
| Massage & Spa Management (setup) | ⬜ | Phase 0 |
| Fish Processing Management (setup) | ⬜ | Phase 0 |

## Phase 2 — Acquisition & Sales
| Module | Status | Depends on |
|---|---|---|
| Leads Management | ⬜ | Person record |
| Reservation Inquiry (receive → approve → bill) | ⬜ | Billing, Package |
| Reservations Calendar & Availability | ⬜ | Availability engine, Rooms/Boats |
| Availability Widget (embeddable) | ⬜ | Availability engine, Multi-site |
| Client-site embeds (talonlodge / alaskaluxurylodge / magnusadventures) | ⬜ | Availability Widget |

## Phase 3 — Pre-Arrival
| Module | Status | Depends on |
|---|---|---|
| Pre-arrival Communications (portal magic-link) | ⬜ | Comms, Auth |
| Guest Portal — profile, flights, allergies/medical, age/gender, emergency contact, activity requests, billing/invoice status, fishing-license upload, photo/video download | ⬜ | Trip, Object storage, Billing |
| Asset Assignment (guests → rooms/boats/guides by day) | ⬜ | Setup inventory, Trip |

## Phase 4 — On-Property
| Module | Status | Depends on |
|---|---|---|
| Daily Agenda Communications | ⬜ | Comms, Assignment |
| Activity & Spa Scheduling (incl. breakfast orders) | ⬜ | Setup, Assignment |
| Fish Caught & Processing (daily catch + weights) | ⬜ | Fish Processing setup, Trip |

## Phase 5 — Post-Stay
| Module | Status | Depends on |
|---|---|---|
| Post-Stay Communications | ⬜ | Comms |
| Satisfaction Survey (native; replaces SurveyMonkey) | ⬜ | Person/Trip |
| Survey Score → appended to guest record | ⬜ | Survey, Person record |
| Stay History (stays, accommodations, boats, activities) | ⬜ | accumulates across all phases |

## Phase 6 — Master-data merge (the hard part)
| Module | Status | Notes |
|---|---|---|
| Import + dedupe reservation / profile-activity / survey systems into one Person record | ⬜ | Uses the tiered matching + merge/undo engine; needs the 3 source schemas in `references/` |

---

## How this stays in sync
Any change to the system (a new module, a renamed capability, a completed build) updates, in the
**same commit**: this file, [`module-map.html`](module-map.html), and — if the data model
changed — [DATABASE_DESIGN.md](DATABASE_DESIGN.md). The map and the roadmap are the two views of
the same truth.
