# Database Design & Schema Guidelines — Talon Lodge Platform

**Engine:** Aurora **MySQL 8** (InnoDB, `utf8mb4`). **ORM/migrations:** Laravel.
**Purpose:** (1) the authoritative relational design, corrected around the developer's
Person/Group/Trip guidance, and (2) the naming/PK/CRUD conventions every table must follow.

This supersedes the Postgres migrations in `db/migrations` — those remain as the validated
*blueprint* (field lists, business rules) and are re-expressed here as Laravel/MySQL tables.

---

## 1. Conventions (the schema guidelines)

*(Conventions confirmed with the developer 2026-08-10.)*

**Tables** — `snake_case`, **plural**, including pivots: **`group_persons`**, `package_rooms`
(plural, not Laravel's singular default). **Field names singular** (`first_name`).

**Every table carries** (audit + soft-delete standard on *all* tables):
- `id` **BIGINT UNSIGNED AI** · `ulid` **CHAR(26) unique** (public/stable id; never expose `id`).
- `active` **TINYINT(1) default 1** — **soft delete = `active = 0`. No hard deletes, ever.**
- `created_at` · `updated_at` · `created_by` · `updated_by` (→ `accounts`: who/when for every row).

**Columns**
- Foreign keys `<singular>_id` (`person_id`). Money `DECIMAL(10,2)`; booleans `TINYINT(1)`.
- Enums = `VARCHAR` + app validation (avoid MySQL `ENUM`); a lookup table when user-configurable.
- Normalized match-key columns for guest matching (see §4).

**Foreign keys & integrity**
- **FK constraints: YES** everywhere (InnoDB).
- **Cascading delete: OFF** (`ON DELETE RESTRICT` / NO ACTION). Deletes are soft (`active=0`), so
  nothing is ever hard-deleted and cascades are unnecessary — disabled to prevent accidents.

**Relationships**
- **Group ↔ Trip is 1:1** — a group is the roster for one dated trip. A repeat visit = **copy the
  group** (new group + trip, members carried over then edited). A person's history = their
  `group_persons` across visits.

**Flexible model (assets · scheduling · profiles) — the developer's recommendation, adopted as hybrid**
- `asset_types` define what a property offers (room, boat, guide, massage, activity, breakfast,
  fish-processing…). `assets` are instances with a **`properties` JSON** column for type-specific
  detail — a new offering needs **no new table**.
- **One scheduling table** `assignments` = **person + asset + trip + date** + status + `details`
  JSON, replacing per-feature tables (spa/breakfast/activity/day-assignment). `details` holds the
  type-specific data (massage length, breakfast items, catch weight…).
- `trip_profiles` keep a small **structured core** (fields used for logic/reports) + a `details`
  JSON for the variable, per-property tail.
- **Meta-schema (structure as data):** `field_definitions` (+ optional `field_groups`) define, **as
  data**, the fields each asset type / profile / assignment carries — so staff and other properties
  add fields with **no migrations**. The JSON bags above are *governed by* these definitions
  (validation, dynamic forms, defaults). See DB_SCHEMA §0.
- **Boundary (why hybrid):** keep the *relational spine* strict — person, group, trip, assignments,
  matching, merge, money, FKs — for integrity + reporting; use JSON (governed by field_definitions)
  only for variable, type-specific attributes. **JSON stays JSON — no generated columns; reporting
  extracts JSON to memory/temp tables on demand (decided 2026-08-10).**

**CRUD**
- Reads scoped by tenant (`lodge_id`) and, for staff, by role (auth phase).
- Destructive actions: soft-delete + confirm; merges get full undo (§4).

---

## 2. The people model (corrected — this is the core fix)

The failure mode on Magnus/Talon was mixing **contact / group / profile / trip**. The clean
separation:

```
persons                 -- one human, forever. Visits many times, under different groups.
├── id, ulid
├── first_name, last_name
├── city, state, country
├── created_at, updated_at, deleted_at
   (contact points normalized: person_emails, person_phones, person_name_aliases — see §4)

groups                  -- a collection of persons on a booking
├── id, ulid, lodge_id
├── name                -- e.g. "Younger party"
├── lead_person_id → persons        -- the group lead
├── -- booking agent (books on the party's behalf; NOT a guest/person record) --
├── booking_agent_name, booking_agent_email, booking_agent_phone, booking_agent_agency  (all nullable)
├── created_at, updated_at, deleted_at
   -- A shared/agent email (one inbox booking for multiple guests) is stored HERE, never merged into
   -- a Person. See MATCHING_RULES.md rule 1 + decision 2.

group_person            -- membership (a person can be in many groups over time)
├── group_id → groups
├── person_id → persons
├── role                -- 'lead' | 'member'
├── PRIMARY KEY (group_id, person_id)

trips                   -- the booking that happens, tied to DATES
├── id, ulid, lodge_id
├── group_id → groups
├── package_id → packages           -- the dated package booked (pre-fills arrival/departure)
├── arrival_date, departure_date, nights
├── status              -- 'inquiry' | 'booked' | 'in_progress' | 'completed' | 'cancelled'
├── created_at, updated_at, deleted_at
   -- ALL reports and scheduled events belong to (group on) this trip.

trip_profiles           -- ONE profile PER PERSON PER TRIP (snapshot, copy-forward)
├── id, ulid
├── trip_id → trips
├── person_id → persons
├── copied_from_profile_id → trip_profiles   -- provenance of the copy-forward
├── -- contact/logistics snapshot --
├── mailing_* , emergency_contact_name/phone
├── arrival_mode, arrival_flight_no, arrival_time, early_hotel
├── depart_transfer_*  (lodge boat/floatplane to Sitka)   -- leg A
├── depart_flight_*    (onward commercial from Sitka)      -- leg B (distinct from A)
├── boot_size, jacket_size, gender, age
├── food_allergies, medical_conditions, special_event  (each: flag + description)
├── created_at, updated_at
   UNIQUE (trip_id, person_id)
   -- New trip => copy the person's most recent trip_profile forward, then let them edit.
   -- History is preserved because each trip keeps its own row.
```

**Why this works:** a Person is stable; a Trip is a dated event; a Profile is a per-trip
snapshot so changing sizes/diet next year never rewrites last year; membership is many-to-many
so someone can travel with different groups across trips.

---

## 3. Assets & day-by-day assignment (absorbs the boat/guide gap)

Persons on a trip are assigned to **assets by day**. One model covers rooms, boats, guides,
vehicles — and gives real double-booking checks (the boat/guide-assignment gap, SPEC §6).

```
asset_types             -- lodge-configurable: Room, Boat, Guide, Vehicle, ...
├── id, lodge_id, name

assets                  -- a schedulable resource
├── id, ulid, lodge_id
├── asset_type_id → asset_types
├── name                -- "Spruce 1", "Boat #3", "Guide: Sam"
├── capacity            -- seats/beds (e.g. boat caps at 6)
├── linked_room_id → rooms (nullable)   -- when an asset IS a room, tie to the Room record
├── created_at, updated_at, deleted_at

person_day_assignments  -- who is on what asset, which day, which trip
├── id, trip_id → trips, person_id → persons
├── asset_id → assets
├── assignment_date     -- the specific day
├── activity_id → activities (nullable)  -- if the assignment is for an activity that day
├── created_at, updated_at
   -- Enforce capacity + no double-booking in the service layer + a covering index on
   -- (asset_id, assignment_date). Rooms are typically assigned for the whole stay; boats/
   -- guides per day.
```

---

## 4. Guest matching, acquisition & merge (points at `persons`)

Same design as the validated Postgres schema (`db/migrations/0006–0008`), MySQL-ified. The
matching tiers are lookup-based and need **no** `pg_trgm`:

```
person_emails (person_id, email, email_normalized, is_primary)   -- Tier 1: exact normalized email
person_phones (person_id, phone, phone_normalized, is_primary)   -- Tier 2: exact phone
person_name_aliases (person_id, first_name, last_name, source)   -- captured on auto-match
nickname_groups (id, canonical) / nickname_aliases (group_id, alias)   -- ~38 seeded groups

inquiries / reservation_requests / brochure_requests / guest_list_entries
   -- each keeps raw captured values + person_id (set by the matching engine; the thing a
   --  merge re-points and an undo reverts)

merge_review_queue (source_person_id, candidate_person_id, reason, status, ...)  -- Tier-3 flags
merge_history (survivor_person_id, kind, loser_snapshot JSON, survivor_snapshot JSON,
               repointed_records JSON, review_queue_id, undone_at, ...)  -- full merge/undo audit
```

- Matching tiers (SPEC §2.2): T1 exact email → auto-link; T2 exact phone + nickname-equiv name
  → auto-link; T3 nickname-equiv + same last name, no email/phone → flag. All exact +
  nickname-table lookups.
- **Typo-fuzzy (optional, later):** MySQL has no `pg_trgm`. If we want "Smyth"/"Smith"
  tolerance beyond the nickname table, add it in Laravel (similarity over a candidate set) or
  a MySQL `ngram` FULLTEXT index. Not required for the specified tiers.
- Merge/undo is the highest-priority safety feature — keep the full snapshot + repointed-ids
  design so any merge (auto or manual) is precisely reversible (SPEC §2.4).

---

## 5. Setup domain (carried over, MySQL-ified)

Lodges, lodge_types (+ `lodge_type_map`), lodge_affiliations, rooms (+ `room_media`),
activities (+ `activity_media`), adventure_category_groups/adventure_categories, species,
package_series, package_feature_tags, packages (+ `package_arrival_days`, `package_species`,
`package_inclusions`, `package_exclusions`, `package_rooms`, `package_activities`).

Field-level detail is already specified in `db/migrations/0002–0005` and validated against the
real data (49 packages). Re-express those as Laravel migrations 1:1, applying §1 conventions
(bigint `id` + `ulid`, soft deletes, FK constraints). `package_rooms.room_id` may reference an
**affiliated lodge's** room — keep that (SPEC §1b).

---

## 6. Settings table (per developer: minimal config files)

```
settings                -- app configuration, editable in-app (NOT secrets)
├── id, key, value (JSON), scope ('global' | 'lodge'), lodge_id (nullable)
├── UNIQUE (key, scope, lodge_id)
```
Secrets (DB creds, API keys, S3 keys) stay in Secrets Manager / env — never in this table.
Everything else (pricing defaults, feature flags, email templates refs, lookup defaults) lives
here so it's changeable without a deploy.

---

## 7. Resolved (design locked 2026-08-10)
- **PK strategy:** ✅ bigint `id` + `ulid` public column.
- **Group ↔ Trip:** ✅ **1:1** — a Group is never reused; a repeat visit copies the group.
  Enforced by `UNIQUE(group_id)` on `trips`.
- **Reports / scheduled events** (breakfast, massage/activity, fish-caught): ✅ all modeled as
  `assignments` (person + asset + date + `details` JSON); reporting extracts JSON on demand.
- **Meta-schema storage:** ✅ JSON governed by `field_definitions` (not EAV); **no generated columns**.
- **Post-merge email degradation:** ✅ demote to booking-agent context, no retroactive unmerge
  (see MERGE_RULES §7).
