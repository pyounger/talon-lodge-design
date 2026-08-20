# Database Schema — Talon Lodge Platform (for review)

**Complete, authoritative table reference.** Aurora **MySQL 8** (InnoDB, `utf8mb4`), Laravel
migrations. Revised per the developer's review (2026-08-10): `properties` naming, audit columns +
`active` soft-delete everywhere, FK-on/cascade-off, plural tables, **Group ↔ Trip 1:1**, and the
**hybrid flexible model** (asset_types + `assets.properties` JSON, one `assignments` scheduler,
`trip_profiles` core + `details` JSON).

Companions: [`DATABASE_DESIGN.md`](DATABASE_DESIGN.md) (conventions + rationale),
[`RECORD_MANAGEMENT.md`](RECORD_MANAGEMENT.md) / [`MATCHING_RULES.md`](MATCHING_RULES.md) /
[`MERGE_RULES.md`](MERGE_RULES.md).

## Conventions (apply to every table — not repeated below)
- `id` **BIGINT UNSIGNED AI** · `ulid` **CHAR(26) unique** (public id; never expose `id`).
- **`active` TINYINT(1) default 1** — soft delete = `active=0`; **no hard deletes**.
- `created_at` · `updated_at` · `created_by` · `updated_by` (→ `accounts`).
- FK constraints **on**; **cascading delete off** (`RESTRICT`). Money `DECIMAL(10,2)`; enums `VARCHAR`+app-validation.
- `?` = nullable · `→` = FK · `uq` = unique · `JSON` = flexible per-type detail.
- **Build order:** A–G first (tenancy, assets, catalog, people, groups/trips/scheduling, intake, matching). Then H surveys, I billing.

---

## 0. Meta-schema — dynamic field definitions  *(structure as data)*
This is the layer that lets staff/other properties define new asset types, their fields, and profile
fields **as data, with no migrations**. Definitions live here; **values live in the governed JSON bag**
on the record (`assets.properties`, `trip_profiles.details`, `assignments.details`), validated and
form-rendered from these definitions. **JSON stays JSON — no generated columns, no schema mutation
from JSON keys.** For reporting, JSON is **extracted into memory / temp tables on demand**
(AI-assisted scripts pivot it), never materialized as physical columns.

**field_groups** — optional form sections · `property_id`?→properties · `target` (asset|trip_profile|assignment|person) · `name` · `sort_order`
**field_definitions** — one row per configurable field
`property_id`?→properties *(null = platform-wide default; set = that property's custom field)*
`target` (asset | trip_profile | assignment | person) · `target_type_id`? *(for assets = `asset_type_id`; null = applies to all of that target)*
`field_group_id`?→field_groups · `key` *(the JSON key it governs)* · `label` · `data_type` (string|text|integer|decimal|boolean|date|datetime|enum|money|url|file|json)
`input_type`? (text|textarea|select|checkbox|date|file|number…) · `required` bool · `sort_order`
`options` JSON *(enum choices)* · `validation` JSON *(min/max/regex…)* · `default_value`? · `help_text`? · `unit`? · `reportable` bool
· uq(property_id, target, target_type_id, key)

- **Values → JSON:** an asset's `properties`, a profile's `details`, an assignment's `details` are
  key/value bags whose allowed keys, types, and validation come from `field_definitions`.
- **Reporting:** `reportable` simply flags a field worth surfacing in reports. Reporting **extracts the
  JSON into memory / temp tables on demand** — **no generated columns, no runtime DDL**. Reporting is
  group/trip-centric, so extraction cost is small at Talon's scale.
- **Decided (locked):** values are **JSON governed by `field_definitions`** — *not* an EAV
  `field_values` table. Simpler at this scale, keeps the relational spine strict and the meta-schema clean.

---

## A. Tenancy & auth
**accounts** — staff logins · `name` · `email` uq · `password_hash` · `role`
**account_properties** — `account_id`→accounts · `property_id`→properties · uq(both)
**properties** — the tenant (a lodge, spa, retreat…) · `name` · `slug` uq · `website_url`? · `contact_email`? · `consumer_email`? · `phone`? · `toll_free`? · `fax`? · `city`? · `state`? · `postal_code`? · `country`? · `summary`? · `at_a_glance_headline`? · `geo_lat/lng`? · `geo_bbox_*`? · `do_not_email/phone/fax/postal_mail/bulk_email/bulk_postal_mail` · `default_pricing_mode` (flat|adult_child) · `child_age_min/max`? · `brand_voice`?
**property_highlights** — `property_id`→properties · `sort_order` · `text`
**property_types** (platform-wide) — `name` uq  ·  **property_type_property** — `property_id` · `property_type_id` · uq(both)
**property_affiliations** — `property_a_id`→properties · `property_b_id`→properties (store a<b) · uq
**settings** — in-app config (NOT secrets) · `key` · `value` JSON · `scope` (global|property) · `property_id`?→properties · uq(key,scope,property_id)

---

## B. Assets — unified resources & offerings  *(the flexible model)*
Rooms, boats, guides, vehicles, massage, activities, breakfast, fish-processing… are all **assets**
of a type, with a JSON `properties` bag for type-specific detail. A new offering needs **no new table**.

**asset_types** — what a property offers · `property_id`→properties · `name` (Room|Boat|Guide|Vehicle|Massage|Activity|Breakfast|FishProcessing…) · `category` (lodging|excursion|service|dining|processing…) · `schema` JSON *(optional: expected `properties` keys, for validation/UI)* · `schedulable` bool
**assets** — an instance · `property_id`→properties · `asset_type_id`→asset_types · `name` · `capacity`? · `properties` **JSON** *(type-specific — e.g. Room: `{occupancy_min,occupancy_max,bedrooms,bathrooms,bed_configuration,matterport_url,photos[]}`; Activity: `{duration,price_arrival_day,price_during_stay,price_departure_day,min_people,max_people,videos[]}`; Boat: `{capacity}`; Massage: `{duration_min,price}`)* · `parent_asset_id`?→assets *(hierarchy / composite offerings — sub-assets of a boat, room, or activity; e.g. a guide tied to a boat)*

**asset_links** — asset↔asset relationships: **capability** ("linked") and **operational** ("assigned")
`asset_id`→assets · `related_asset_id`→assets · `relation` (guides|captains|crews|includes|…) · `trip_id`?→trips · `assignment_date`? · `properties` JSON · uq(asset_id,related_asset_id,relation,trip_id,assignment_date)
- **Capability** (trip_id/date null): guide → activity ("guides"); captain → boat ("captains"); deckhand → boat ("crews").
- **Operational** (trip_id/date set): this captain + deckhand on this boat for a trip; this guide on this activity that day.

> JSON stays JSON — no generated columns. When a report needs these values, extract the JSON bag into
> a temp table on demand (AI-assisted). Reporting is group/trip-centric, so this is cheap at Talon's scale.

### Asset-type catalog (Talon) — `properties` keys governed by `field_definitions`
| asset_type | category | `properties` (JSON) |
|---|---|---|
| **Room** | lodging | `description`, `photos[]`, `occupancy_min/max`, `bedrooms`, `bathrooms`, `bed_configuration`, `matterport_url` |
| **Activity** | excursion | `description`, `photos[]`, `duration`, `price_arrival_day/during_stay/departure_day`, `min/max_people` |
| **Boat** | excursion | `description`, `photo`, `capacity` (for display + crew assignment) |
| **Guide** | crew | `bio`, `photo` — linked to Activities via `asset_links` (relation `guides`) |
| **Captain** | crew | `bio`, `photo` — linked to Boats (`captains`) |
| **Deckhand** | crew | `bio`, `photo` — linked to Boats (`crews`) |
| **Breakfast** | dining | `description`, `photo` — **4–5 options/day**; a 4-night package includes **4** breakfast selections (one per morning) |
| **Beverage** | dining | `description`, `photo`, `pack_size` (6), `unit_price` — **beer sold by the 6-pack**, ordered for a boat |

**Ordering flows (via guest `assignments`, person + asset + date):**
- **Breakfast:** each morning a guest picks one Breakfast option → `assignment(person, breakfast_asset, date)`. Package covers `nights` breakfasts.
- **Beverage:** 6-pack orders for a boat day → `assignment(person, beverage_asset, date, details:{packs:N, boat_asset_id})`.

---

## C. Catalog & packages  *(relational — the sellable products)*
**adventure_category_groups** — `name` uq  ·  **adventure_categories** — `group_id`?→adventure_category_groups · `name` · `uses_species` bool  ·  **species** — `name` uq
**package_series** — `property_id`→properties · `name` · `rate_increase_per_person` dec · `description`? · uq(property,name)
**package_feature_tags** — `label` uq
**packages** — `property_id`→properties · `slug` · `title_override`? · `package_series_id`?→package_series · `adventure_category_id`?→adventure_categories · `status` (draft|published|archived) · `available_on_website` bool · `description`? · `details`? · `fees_and_terms`? · `notes`? · `pricing_mode`? · `arrival_start/end_date`? · `booking_start/end_date`? · `nights`? · `adventure_days_min/max`? · flat: `deposit_amount`/`surcharge_per_person`? · adult_child: `deposit_adult/child`,`surcharge_adult/child`? · uq(property_id,slug)
**package_arrival_days** — `package_id` · `day_of_week` (0–6) · uq(both)
**package_species** — `package_id` · `species_id` · uq(both)
**package_inclusions** / **package_exclusions** — `package_id` · `feature_tag_id` · uq(both)
**package_assets** — replaces package_rooms + package_activities · `package_id`→packages · `asset_id`→assets *(room or activity; may belong to an affiliated property)* · `rate_per_person`? · `rate_adult`? · `rate_child`? · `is_included` bool · `overrides` JSON *(e.g. occupancy overrides)* · uq(package,asset)

---

## D. People — the master record  *(authored)*
**persons** — durable person-level attributes *(per-visit detail lives in `trip_profiles`)*
`first_name`? · `middle_name`? · `last_name`? · `suffix`? · `preferred_name`?
`person_status` (prospect|active|inactive|deceased|banned|merged|test) *(classification — separate from the `active` soft-delete flag; excludes staff/agent, which aren't persons)*
`canonical_name` VARCHAR — **app-maintained on write** = `lower(first_name)_lower(last_name)` *(indexed; fast search/sort/report — NOT a DB generated column; nickname-aware matching still uses the `nickname_groups` lookup)*
`photo_url`? *(object storage — recognition headshot)* · `photo_source`? (imported|lodge_capture) · `photo_captured_at`?
`address_line_1/2`? · `city`? · `state`? · `postal_code`? · `country`? · `date_of_birth`? · `gender`?
`emergency_contact_name/phone`? · `marketing_opt_in`? · `do_not_email/phone/postal_mail/bulk_email`
`how_heard`? · `source_first_seen`? · `first_seen_at`? · `past_guest` · `vip` · `internal_notes`?
*rollups:* `total_trips`? · `total_nights`? · `first_stay_date`? · `last_stay_date`? · `lifetime_spend` dec? · `latest_survey_score` dec? · `avg_survey_score` dec? · idx(last_name), idx(canonical_name)
> Contact/compliance flags (`do_not_*`, `marketing_opt_in`, `vip`, `past_guest`) stay as **columns** (queried + compliance). Property-custom person fields go via the meta-schema `person` target (§0), not a loose JSON bag.
**person_emails** — `person_id` · `email` · `email_normalized` idx · `is_primary` · `is_shared_agent`
**person_phones** — `person_id` · `phone` · `phone_normalized` idx · `is_primary`
**person_name_aliases** — `person_id` · `first_name`? · `last_name`? · `source`
**nickname_groups** — `canonical` uq  ·  **nickname_aliases** — `nickname_group_id` · `alias` · uq(group,alias) · idx(alias)

---

## E. Groups · Trips · Profiles · Scheduling
**groups** — the roster for **one** trip · `property_id`?→properties · `name`? · `lead_person_id`?→persons · `booking_agent_name/email/phone/agency`? *(agent, not a person)* · `communications_mode` (each|lead|agent) default `each` *(group-wide comms routing — see note)* · `copied_from_group_id`?→groups *(repeat visit = copy)*
**group_persons** — membership · `group_id`→groups · `person_id`→persons · `role` (lead|member) · uq(group,person)
**trips** — the dated booking (**1:1 with group**) · `group_id`→groups **uq** · `property_id`?→properties · `package_id`?→packages · `arrival_date`? · `departure_date`? · `nights`? · `status` (inquiry|booked|in_progress|completed|cancelled)
**trip_profiles** — one per person per trip; **structured core + `details` JSON** (copied forward)
`trip_id`→trips · `person_id`→persons · `copied_from_profile_id`?→trip_profiles · `version` int *(1,2,3… across copy-forwards)*
core: `arrival_mode`? · `arrival_flight_no`? · `arrival_time`? · `depart_transfer_time`? · `depart_flight_no`? · `depart_flight_time`? · `emergency_contact_name/phone`? · `communications_email`? *(per-guest override; null → group routing)*
`details` **JSON** *(the variable tail — boot/jacket size, allergies-as-of-trip, medical, special-event, per-property custom fields)* · uq(trip_id,person_id)

> **Communications routing.** Every guest has an effective comms address, resolved as: `trip_profiles.communications_email` if set → else by `groups.communications_mode` — `each` = the person's own email, `lead` = the lead person's email, `agent` = `groups.booking_agent_email` (the event planner / travel agent). Itineraries, reminders, and invoices all send to the resolved address; respect `persons.do_not_email`.
**assignments** — the **one scheduler**: person + asset + date (replaces day-assignments, breakfast_orders, spa_appointments, activity scheduling)
`trip_id`→trips · `person_id`→persons · `asset_id`→assets · `assignment_date` date · `status` (requested|confirmed) · `details` **JSON** *(type-specific — massage length, breakfast items, fish caught `{species,weight,count}`…)* · idx(asset_id,assignment_date)
**stay_media** — guest uploads + stay photos/videos (object storage) · `trip_id`→trips · `person_id`?→persons · `kind` (fishing_license|photo|video|document) · `url` · `caption`? · `uploaded_by` (guest|staff) · `available_for_download` bool

---

## F. Acquisition & intake  (raw values + `person_id` set by matching)
**inquiries** — `property_id`? · `person_id`? · name/email/phone · `message`? · `form_name`? · `website`?
**leads** — `property_id`? · `person_id`? · name/email/phone · `state`? · `form_name`? · `website`? · `stage`
**reservation_requests** — `property_id`? · `person_id`? · `package_id`? · `arrival_date`? · name/email/phone · `notes`?
**brochure_requests** — `property_id`? · `person_id`? · name/email · address · `num_fishing/non_fishing_guests`? · `times_to_alaska_before`? · `purpose_of_travel`? · `main_package_interest`? · `opt_in_offers`? · `how_heard`?
**guest_list_entries** — `group_id`→groups · `person_id`? · name/email · `past_guest`?

---

## G. Matching & merge  *(authored — see MERGE_RULES.md)*
**merge_review_queue** — `source_person_id`? · `candidate_person_id`? · `reason` · `status` (pending|merged|not_a_match) · `resolved_by`?→accounts · `resolved_at`? · idx(status)
**merge_history** — `survivor_person_id`→persons · `loser_person_id`?→persons *(deactivated on merge)* · `kind` (auto|manual) · `survivor_snapshot` JSON · `loser_snapshot` JSON · `repointed_records` JSON · `review_queue_id`? · `performed_by`? · `undone_at`? · `undone_by`? · idx(survivor,undone_at)
**person_ulid_redirects** — `ulid` uq · `person_id`→persons · `merge_history_id`? *(old loser ulid → survivor, so links still resolve)*

---

## H. Surveys & satisfaction  *(replaces SurveyMonkey)*
**surveys** — `property_id`? · `name`  ·  **survey_questions** — `survey_id` · `prompt` · `type` (rating|text|choice) · `sort_order`
**survey_invitations** — `survey_id` · `trip_id`? · `person_id` · `token` uq · `sent_at`? · `completed_at`?
**survey_responses** — `survey_invitation_id` · `question_id` · `answer`? · `score`?
**survey_scores** — the per-guest score on the record · `person_id` · `trip_id`? · `survey_id` · `score` dec · idx(person_id)

---

## I. Billing  *(Stripe, designed fresh)*
**invoices** — `trip_id`? · `group_id`? · `bill_to_person_id`? · `status` (draft|sent|paid|void) · `subtotal`/`taxes`/`total`/`balance` dec
**invoice_line_items** — `invoice_id` · `description` · `quantity` · `unit_price` dec · `amount` dec · `source_type`? · `source_id`?
**payments** — `invoice_id` · `amount` dec · `method` · `status` · `processed_at`? · `external_ref`? (Stripe)

---

## Relationship spine
```
person ─┬─< person_emails/phones/name_aliases
        ├─< group_persons (role) >─ group ─1:1─ trip ─< trip_profiles (core + details JSON)
        │                                     └─< assignments >─ assets (asset_type + properties JSON)
        │                                          trip ─ package ─< package_assets >─ assets
        ├─< inquiries/leads/reservation_requests/brochure_requests/guest_list_entries
        ├─< survey_scores · stay_media · invoices
        └─< merge_history (survivor)          group ── booking_agent_* (not a person)
```
Everything points at one `person`. Rooms/boats/guides/massage/activities are all `assets`; anything
scheduled is an `assignment` (person + asset + date); type-specific detail lives in JSON, the
relational spine stays strict.
