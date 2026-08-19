# Lodge Platform Rewrite — Phase 1 Spec
## Data Model & Admin Setup: Account, Lodge, Room, Activity, Package

*Derived by working backward from the live talonlodge.com public site, reconciled against the legacy Magnus Adventures admin screens. Talon Lodge used as the reference implementation; model is multi-tenant by design.*

---

## 1. Account & Lodge

```
Account
├── id (PK)
├── username
├── password_hash
├── created_at / updated_at

AccountLodge                          // join table — one account can manage multiple lodges
├── account_id (FK → Account)
├── lodge_id (FK → Lodge)

Lodge
├── id (PK)
├── name
├── slug
├── website_url
├── contact_email                      // internal / where staff notifications go
├── consumer_email                     // public-facing "where consumer sends email"
├── phone, toll_free, other_phone, fax
├── address_line_1 (tagline/marketing subtitle — legacy usage, not a real street address)
├── city, state_or_province, postal_code, country
├── summary (text)
├── at_a_glance_headline
├── geo_point (lat, lng)               // map pin
├── geo_bounding_box (sw_lat, sw_lng, ne_lat, ne_lng)   // map zoom extent
├── do_not_email / do_not_phone / do_not_fax / do_not_postal_mail / do_not_bulk_email / do_not_bulk_postal_mail
├── default_pricing_mode ('flat' | 'adult_child')
├── child_age_min (nullable)
├── child_age_max (nullable)
├── created_at / updated_at

LodgeHighlight                        // replaces legacy fixed "At A Glance Line1–5"
├── lodge_id (FK → Lodge)
├── sort_order
├── text
```

**Confirmed:** Talon Lodge and The Bluff House at Talon Lodge are both real, independent `Lodge` records under a single shared `Account`. No sub-account hierarchy — one login manages both.

```
LodgeAffiliation                      // symmetric, multi-directional cross-listing
├── lodge_a_id (FK → Lodge)
├── lodge_b_id (FK → Lodge)
├── created_at
```

Guests on either lodge's public site see and can book both lodges' availability. Query both directions (`lodge_a_id = X OR lodge_b_id = X`) to resolve a lodge's full affiliated set.

**Booking attribution:** every `Booking`/`Reservation` (Phase 2) carries its own `lodge_id` (whichever lodge's room/package was actually booked). Since Bluff House and Talon share one `Account`, there is no separate attribution problem — all bookings, regardless of which site they were made on, are visible to the one shared account.

---

## 2. Room (lodging inventory — split from legacy "Resource")

```
Room
├── id (PK)
├── lodge_id (FK → Lodge)
├── name
├── room_type (FK → RoomType, lodge-configurable lookup: Room | Cabin | House | Suite...)
├── occupancy_min (int, required)     // e.g. Spruce 1 = 2, Main Spruce = 6
├── occupancy_max (int, required)
├── description (text)
├── matterport_url (nullable)
├── created_at / updated_at
```

Note: "double occupancy" is a **pricing convention** (rate assumes 2 guests share), not a literal cap — `occupancy_min`/`max` define real physical capacity per room, independent of how the rate is priced.

---

## 3. Activity (non-lodging bookable service — split from legacy "Resource")

```
Activity
├── id (PK)
├── lodge_id (FK → Lodge)
├── name                              // "Extra Fishing Day", excursions, rentals
├── activity_type (FK → ActivityType, lodge-configurable lookup: Guide | Excursion | Rental...)
├── duration (nullable)
├── capacity (nullable int)
├── created_at / updated_at
```

---

## 4. Adventure Category (two-level, shared platform-wide lookup)

```
AdventureCategoryGroup
├── id
├── name                              // "Fishing"

AdventureCategory
├── id
├── group_id (FK → AdventureCategoryGroup, nullable)
├── name
├── uses_species (bool)               // drives conditional Species field in admin
```

**Talon Lodge's actual categories:**

| Group | Category | uses_species |
|---|---|---|
| Fishing | Sportfishing | true |
| Fishing | Freshwater Fishing | true |
| Fishing | Alaska Adventure Combo | true |
| *(none)* | Adventure Viewing | false |

`Adventure Viewing` is a flat leaf category with no sub-types (unlike Fishing). Other lodges on the platform may define entirely different groups/categories (e.g., a hunting lodge) — this table is shared and open-ended.

```
Species                               // shared, platform-wide lookup
├── id, name                          // King Salmon, Silver Salmon, Arctic Char...
```

---

## 5. Package (the central entity)

```
PackageSeries                         // lodge-owned lookup: Standard, Chef Series, Winemaker Series
├── id, lodge_id, name

Package
├── id (PK)
├── lodge_id (FK → Lodge)
├── slug
├── title_override (nullable)         // if null, auto-generate from dates + adventure_days + name
├── package_series_id (FK → PackageSeries, nullable)
├── adventure_category_id (FK → AdventureCategory, NULLABLE)   // package may be lodging-only
├── status ('draft' | 'published' | 'archived')                // explicit lifecycle, replaces
│                                                                 // reliance on date-filtering alone
├── available_on_website (bool)
├── description (rich text)
├── details (rich text)               // logistics/policy text block
├── fees_and_terms (rich text)        // site merges Fees + Terms into one displayed block
├── notes (text, internal only)
├── landing_page (url, nullable)
├── special_offer_id (FK, nullable)
├── pricing_mode (nullable: 'flat' | 'adult_child')   // inherits Lodge.default_pricing_mode if null
├── arrival_start_date / arrival_end_date
├── booking_start_date / booking_end_date
├── arrival_time_earliest / latest
├── departure_time_earliest / latest
├── arrival_travel_days / departure_travel_days
├── min_days_before_booking / max_days_before_booking
├── adventure_days_min / adventure_days_max
├── child_age_min_override / child_age_max_override (nullable — else inherits Lodge)
│
│  -- flat pricing mode --
├── deposit_amount (decimal, per person)
├── surcharge_per_person (decimal — charged when booking is below a room's occupancy_min)
│
│  -- adult_child pricing mode --
├── deposit_adult / deposit_child (decimal)
├── surcharge_adult / surcharge_child (decimal)
│
├── created_at / updated_at
```

**Computed, not stored:**
- `display_price_min` / `display_price_max` = MIN/MAX of `PackageRoom.rate_per_person` (or `rate_adult`) across linked rooms
- `min_people` = MIN of `PackageRoom.occupancy_min` across linked rooms

```
PackageArrivalDay                     // which weekdays arrival is permitted
├── package_id, day_of_week

PackageSpecies                        // many-to-many — ONLY relevant/shown when
├── package_id, species_id            //   adventure_category.uses_species = true

PackageFeatureTag                     // shared lookup: Accommodations, All Meals, Alcohol...
├── id, label

PackageInclusion (package_id, feature_tag_id)
PackageExclusion (package_id, feature_tag_id)
```

### Package ↔ Room

```
PackageRoom
├── package_id, room_id
├── rate_per_person (flat mode)
├── rate_adult / rate_child (adult_child mode)
├── occupancy_min_override / occupancy_max_override (nullable — package-specific override
│      of the Room's base occupancy)
```

### Package ↔ Activity (add-on activities)

```
PackageActivity
├── package_id, activity_id
├── rate_per_person (nullable)
├── is_included (bool)                // bundled into package price vs. optional paid add-on
```

Confirmed: a Package can have **no** `adventure_category_id` (pure lodging) and **still** attach optional add-on Activities via `PackageActivity` — the two are independent.

---

## 6. Admin Setup Screen — field visibility rules

| Field / Section | Shown when |
|---|---|
| Adult/Child rate & deposit fields | `pricing_mode = 'adult_child'` (resolved from Package, else Lodge default) |
| Flat rate & deposit fields | `pricing_mode = 'flat'` |
| Species selector | `adventure_category_id` is set AND that category's `uses_species = true` |
| Adventure Category selector | Always shown, but optional (nullable) |
| Package Activities (add-ons) | Always available, regardless of adventure category presence |
| Child age range override | Only relevant if `pricing_mode = 'adult_child'` |

---

## 7. Known legacy data-quality issues to handle during migration (not to replicate)

- Duplicate Room names with conflicting occupancy values across screens (e.g. "Bluff House" recorded as 5/6, 4/4, and 6/6 in different places) — reconcile per room during migration; the new schema has one `occupancy_min`/`max` per Room with package-level overrides where legitimately needed.
- Literal `""` string stored in Address Line 2 — clear on migration.
- Test/junk rows ("testresource", "demo22July") — exclude from migration.
- Stale packages with no lifecycle flag (e.g., a 2020 package still surfacing in "related packages" on the live site) — `status = 'archived'` now makes this explicit rather than relying on date math.
- "Bluff House" previously double-modeled as both a Room (under Talon) and — correctly — its own Lodge. Migration should remove the Room-level Bluff House entries once confirmed redundant with the standalone Lodge record.

---

## 8. Open for next phase

This spec covers Lodge/Room/Activity/Package setup only. Next phase (Inquiry → Lead → Reservation Request → Booking) will need to define:
- How a `Booking` references `Package`, `PackageRoom`, and optionally `PackageActivity`
- Whether Inquiries/Leads carry `lodge_id` only, or need cross-lodge tagging given the affiliation/shared-account structure
- Funnel stage transitions and what data is captured at each stage
