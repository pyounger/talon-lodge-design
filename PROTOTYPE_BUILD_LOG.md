# Talon Lodge — Scheduling & Guest-Experience Prototypes · Build Log

_Last updated: 2026-08-14_

## What this document covers
This log documents the **clickable HTML/JS prototypes** in `docs/` that define the
scheduling, boat-assignment, approval, daily-reporting and guest-portal behavior for the
Talon Lodge Platform. They run entirely in the browser on **`localStorage`** and are wired
together through a single **Test Hub** so they share one dataset.

> **Framework note (read this first).** These are **prototypes / behavioral specs**, *not*
> the production build. Andy's requested framework is **Laravel (Aurora MySQL) + Angular/Daxa**
> with the locked **v4 schema** (Person → Group → Trip → per-trip Profile → **Assignments**,
> meta-schema `field_definitions`, unified **assets** model). The production code for the data
> layer (persons/groups/trips/assignments, matching, merge, packages, billing, surveys) already
> lives in this same repo under `app/` + `database/` and is pushed to `talon-lodge-api`.
> **The scheduling / boat / spa / portal behavior in `docs/` has NOT yet been implemented in
> Laravel/Angular** — see "Mapping to Andy's framework" and "Port checklist" below. The
> prototypes are the source of truth for *how it should behave*; the framework is where it gets
> built for production.

---

## The Test Hub (13 tools)
`docs/test-hub.html` embeds every tool (base64) and loads each into an iframe on one origin, so
all tools share the same `localStorage`. Regenerate after any tool change with
`node build-hub.js` (script in the session scratchpad; source list below).

| Group | Tool | File | Purpose |
|---|---|---|---|
| Admin setup | Team | `team-admin.html` | Guides, therapists, boats & crew (multi-boat captains, per-boat capacity) |
| Admin setup | Activities | `activities-admin.html` | Add-ons, pricing, offering channel, available times |
| Admin setup | Packages | `packages-admin.html` | Trip dates, series, rates |
| Admin setup | Settings | `settings-admin.html` | Deposit, fees, cancellation policy |
| Admin setup | Vendors | `vendors-admin.html` | Pilots & outside providers |
| Operate | Scheduling | `scheduling-demo.html` | Availability engine + master resource calendar |
| Operate | Approvals | `approvals.html` | Approve activity & spa requests (assign guide/therapist/pilot/boat/time) |
| Operate | Boat assignments | `boat-assignments.html` | Home boat per guest + per-day switching + daily manifest |
| Operate | Daily report | `daily-report.html` | Per-date "Boat & Activity Schedule" run sheet, by individual |
| Guest | Reservation | `booking-engine.html` | The 9-step guest booking flow |
| Guest | Guest Portal | `guest-portal.html` | Per-guest self-service trip home, requests & status |
| Reference | Test data | `test-data.html` | Loads the 24-guest full-lodge roster |
| Reference | Test guide | `test-guide.html` | Step-by-step test scripts |

---

## Data model — `localStorage` keys
Every tool reads/writes these shared keys. This is the prototype equivalent of Andy's schema.

| Key | Shape | Meaning |
|---|---|---|
| `talon_team_v1` | `{guides,therapists,captains,deckhands,boats}` | Team/crew; each boat has `capacity` |
| `talon_activities_v1` | `[{id,name,times,offer,availability,status,…}]` | Activity catalog (incl. offering channel) |
| `talon_packages_v1` | `[{id,series,category,arrival_start_date,nights,…}]` | Published packages (trip dates) |
| `talon_settings_v1` | `{deposit,…}` | Deposit/fees/policy |
| `talon_vendors_v1` | `{pilots,processors,transport}` | Outside vendors |
| `talon_portal_profile` | `{ "Group\|pkgId": {mode, guests:[…]} }` | **Rosters** — the per-guest records (name, email, room, boatPref, diet, sizes, access) |
| `talon_portal_requests` | `[{id,group,actId,name,date,guests,guestNames,kind,status,source}]` | Activity/spa requests awaiting approval |
| `talon_bookings_v1` | `[{id,date,actId,name,group,guestNames,time,assigneeType,assigneeName,guideIds,boatIds,boatId,crew,treatment,…}]` | **Confirmed bookings** — every one carries the individual `guestNames` |
| `talon_boat_seating` | `{ [arrivalDate]: { "group::name": boatId } }` | **Home boat** per guest for the whole trip |
| `talon_boat_daily` | `{ [specificDate]: { "group::name": boatId } }` | **Per-day boat override** — a guest riding a different boat that day |
| `talon_saltcap` | number | Saltwater trips/day cap |
| `talon_portal_trip` | `{group,pkgId,party,lead,viewGuest}` | Which trip/guest the portal is viewing |

---

## Behavior implemented this session (the rules)

### Everything funnels to the individual
The guiding principle (Phil, 2026-08-14): **every assignment, activity, and the guest's
history/profile attaches to the individual person, not just the group.** The group is only how
people book. Consequently:
- Confirmed bookings store `guestNames` (and per-guest `guestName`/`treatment` for spa).
- Reports and calendars list **people**, not just the group name.

### Boats
- **Home boat** per guest for the trip (`talon_boat_seating`); groups can share a boat and split
  across boats (cross-group filling up to a boat's capacity).
- **Per-day switching** (`talon_boat_daily`): a "Switch boats by day" grid (guest × adventure-day,
  a boat dropdown per cell, gold = override). Honored by the Daily Report, Scheduling master
  calendar, and the guest's portal agenda.
- **Over-capacity is accepted, not blocked** — putting a guest on a full boat (home assignment
  *or* per-day switch) is allowed; the boat is flagged **"⚑ over by N — switch someone off"**
  (salmon highlight) in the manifest, the switch grid, and the Daily Report. Built for large
  groups that rotate boats daily.
- **Per-boat capacity** comes from Team (a boat may be 6, 4, or 2).

### Activity priority
- On a day a guest has a booked **adventure** (ATV, kayak, whale, hiking, freshwater) **or a
  Day Spa**, they come **off the boat** that day (per person).
- **Evening Massage** does *not* remove them — they still fish during the day.

### Captain–guide conflict (one person, two roles)
- A person can be **both a guide and a boat captain** (e.g. Travis, Gavin). If that person's boat
  is **fishing that day** — regular sportfishing (guests seated on it) *or* an Additional Saltwater
  charter — they are **removed from the guide pool** for that day and can't be assigned any adventure.
- Enforced in the availability engine (`freeGuides`), the Approvals guide picker/auto-assign
  (marked "· running boat"), and shown on the Scheduling calendar ("🚤 Roamer · sportfishing").
- Guide↔captain are linked by name (full or first-name match) in the prototype; in Andy's schema
  this is naturally one **Person** with both guide- and captain-asset capabilities.

### Saltwater (Additional Saltwater Day)
- Travel-day charter, **4–6 guests per boat**, crew from the fleet (delivery boats excluded).
- **Cross-group filling**: add individuals from any group to a boat up to 6; per-guest removal;
  a full boat drops out of the picker; boats under 4 flagged "needs N more".
- A group already booked shows "✓ Booked" (no phantom availability); party > 6 is blocked.
- **Never auto-deleted.** Booking an adventure never removes an existing saltwater trip. Deleting a
  scheduled trip — the whole trip *or* its last remaining guest — requires an explicit confirm;
  removing one of several guests is a normal roster edit. (A captain is only freed to guide when his
  boat has *no* fishers that day, i.e. the whole group moved to an adventure and no one else was aboard.)

### Spa
- **Massage** — evening, 4 slots/day (2 therapists × 2 times), first-two-at-4:30 / next-two-at-5:30
  rule, editable times, per-guest therapist + treatment. Stays on the boat.
- **Day Spa** — daytime (10 AM–2 PM), 2 guests/day, staffed separately. **Pulls the guest off the
  boat** like an adventure. Shows in Scheduling and the Guest Portal Spa module.

### "Enjoying the Island"
- Any guest on a stay day with **no boat and no activity/spa** is auto-classified **"Enjoying the
  Island"** — shown as its own section in the Daily Report (grouped by group) and on the guest's
  portal agenda ("a free day to explore"). Clears automatically once they get a boat or activity.

### Approvals
- Every request (from Reservation or Portal) lands in the queue with a 24-hour SLA clock.
- Approving assigns the resource (guide / therapist+treatment / pilot+guide / boat+crew) and a
  time, writes a confirmed booking carrying the individual name(s), and consumes the resource.
- **Declining removes the request** from the queue entirely (only requested & approved show).

### Guest Portal
- Demo switcher: **Package · Group · Guest**. Selecting a guest shows **their own portal**
  (their details form, their license, their agenda, their booked activities).
- Agenda shows, per stay day: their **home sportfishing boat**, any **adventure/spa** (which
  replaces the boat), evening **massage** alongside, and **Enjoying the Island** on free days.

### Test data
- `test-data.html` loads the real **24-guest full-lodge roster** (6 groups) onto the existing
  **"arrive May 24" package** without clobbering Package Management. Writes rooms
  (`talon_rooms_v1`), profiles, and a handful of pending requests.

---

## Mapping to Andy's framework (v4 schema)
The prototype maps cleanly onto the locked production model — nothing here contradicts it:

| Prototype (localStorage) | Production (Laravel v4 schema) |
|---|---|
| `talon_portal_profile` guests | `persons` + `group_persons` + per-trip `trip_profiles` (core + `details` JSON) |
| `talon_boat_seating` (home boat) | `assignments` (person + boat-asset + trip, no date = trip-wide) |
| `talon_boat_daily` (per-day switch) | `assignments` (person + boat-asset + trip + **date**) |
| `talon_bookings_v1` (activities/spa/saltwater) | `assignments` (person + activity/spa-asset + trip + date + `details` JSON: time, guide, treatment, crew) |
| boats / guides / therapists / activities | `assets` (`asset_type` + `properties` JSON) + `asset_links` (guide→activity, captain/deckhand→boat) |
| "Enjoying the Island" | **derived** — a person with no assignment on a stay date (no table needed) |
| over-capacity flag | validation/report layer over `assignments` vs asset capacity |

The unified **"asset assigned to person per day"** model Andy locked is exactly what the boat
switching, day-spa, and activity-priority logic here assume. So these prototypes are a faithful
behavioral spec for the `assignments` scheduler + the Angular operations UI.

## Port checklist (prototype → framework)
Not yet built in Laravel/Angular:
1. **Assignment scheduler UI** (Angular/Daxa): boat board with per-day switching + over-capacity
   flags; the availability grid; approvals queue.
2. **Availability engine** (server): guide = 1 activity/day for ≤3; massage 4 slots/day; day spa
   2/day; saltwater 4–6/boat; per-boat capacity; activity-priority pull-off.
3. **Daily "Boat & Activity Schedule"** report endpoint (by individual, incl. Enjoying the Island).
4. **Guest portal** (per-guest magic-link) reading the same assignments.
5. Seed the asset catalog (boats/guides/therapists/activities incl. Day Spa) via `AssetCatalogSeeder`.

---

## Where things live / backup
- **Repo:** `talon-lodge-platform` (local) → GitHub `pyounger/talon-lodge-api` (`main`).
- **Prototypes:** `docs/*.html` (+ `docs/*.md` specs). Production code: `app/`, `database/`.
- **Test Hub artifact:** https://claude.ai/code/artifact/50d7ff72-be84-46c5-a348-3bf8465efc41
- All session work is committed on `main`; see `git log`. A dated ZIP of `docs/` is also kept in
  Downloads as an offline snapshot.
