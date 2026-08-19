# Matching Business Rules — derived from real data

Rules for building **one master `Person`** and its lead / inquiry / reservation / profile
history, derived from a matching pass over four real 2026 exports (inquiries, leads,
package-group bookings, guest list — **2,706 rows**). Pairs with
[`RECORD_MANAGEMENT.md`](RECORD_MANAGEMENT.md) (the process) and DATABASE_DESIGN §4.

> The detailed run (with real emails/phones) is kept **local only** (not committed) for privacy.
> This file is the PII-free ruleset the build follows.

## What the run showed (Tier 1/2 email+phone only)
| Metric | Value | Meaning |
|---|---|---|
| Raw rows | 2,706 | inquiries 1000 · leads 1000 · bookings 139 · guests 567 |
| Master persons (email/phone merge only) | 2,481 | contact-based merge alone barely dents the total |
| Persons in 2+ source types | 90 | most records don't yet connect across sources |
| Name-only persons (no email/phone) | 1,115 | almost all inquiries — unmatchable by contact |
| Name-only records matching a contactful person by name | 859 | the attach opportunity |
| Bookings with no contact to link to | 19 | booker name unmatched |
| Shared-email across different last names | 16 | **travel agents / shared inboxes — over-merge trap** |
| Household phones (same phone, different people) | 35 | couples/family — correctly not merged |

**Conclusion:** email/phone matching is correct but only covers sources that *carry* contact
info. The real leverage is (a) attaching name-only inquiries/bookings to the right person, (b)
linking bookings→groups→guests, and (c) not letting shared/agent emails fuse different guests.

---

## Identity signals & reliability (observed)
| Signal | Reliability | Caveat from the data |
|---|---|---|
| Email | High | Can be an **agent/assistant/shared inbox** (16 cases, incl. travel agencies) → not always the guest |
| Phone | High **with name** | Shared within households (35) → needs a name match too |
| Name | Low alone | Nicknames + spellings + common names; 1,115 name-only rows |

---

## The rules

### Matching tiers
1. **Tier 1 — exact email → auto-link.** **Guardrail:** if an email maps to **≥2 distinct people**
   (different name keys), it is a **shared/agent inbox** — do *not* merge those people. Record it as
   the **booking-agent contact on the relevant Group** (decision 2), not as anyone's identity, and
   flag for review. *(Driver: travel-agency inboxes booking for multiple guests.)*
2. **Tier 2 — exact phone + nickname-equivalent name → auto-link.** Validated by the real case of two
   different emails unified by one shared phone. Phone alone with **different** names = household →
   do not merge (optionally record a household link).
3. **Tier 3 — name only (nickname+last), no email/phone → never auto-merge.** Resolve by count of
   contactful matches:
   - **Exactly one** contactful person with that name → **auto-attach** the inquiry/booking as history.
   - **Multiple** (common name) → **review queue**.
   - **None** → keep as an unlinked inquiry/lead; link later when contact arrives.
4. **Nicknames & spelling.** Maintain the nickname table + normalize (lowercase, trim, collapse
   spaces, strip punctuation, extract parentheticals like "Raymond(Eddie)" as an alias). **Ambiguous
   nicknames** (Pat, Chris, Alex, Sam, Jamie, Terry, Lee, Jean) are **not** auto-canonicalized —
   they require last name + a second signal. Capture every variant as an alias on the master.

### Booking ↔ group ↔ guest linkage (the gap the data exposed)
5. **Booking → person.** Bookings carry no contact. Link the booker to a person by name match to
   **exactly one** contactful person, corroborated by rule 6. Multiple/none → review. Every booking is
   a **reservation-history** entry; **multiple bookings by one person = multiple trips — never dedupe
   trips** (one guest here has two 2026 bookings).
6. **Group membership by Group name + arrival date.** Join the guest list to a booking on
   **group name + arrival date** (validated: "Younger Group" + 5/1/2026 ↔ that booking). The booker
   becomes the group **Lead**; guest-list rows become **Members**. When the lead has their own
   guest-list row, its email anchors the otherwise-contactless booking. **Never infer identity from a
   shared email domain** (e.g. two people at the same company domain are still two people).
7. **Role is per-membership, not per-person.** A member in one group/year can be a lead in another;
   history only accumulates.

### Import hygiene
8. **Inquiries:** scan the free-text comment for an email/phone to upgrade matchability before
   falling back to Tier-3 name attach/review.
9. **Parsing:** handle no-header / junk-header files, BOM, multi-line quoted comments, junk columns,
   blank group values (40 rows), phone-format variance, and parenthetical nicknames.
10. **Safety:** every merge is reversible; shared/agent-email and common-name cases go to **review**,
    never silent auto-merge.

---

## Decisions (locked 2026-08-09)
1. **Auto-attach — YES.** A name-only inquiry/booking that matches **exactly one** contactful person
   attaches automatically; only ambiguous names (2+ candidates) go to review.
2. **Booking agent — modeled on the GROUP.** A shared/agent email never merges guests; instead the
   Group carries a **booking-agent** section (name, email, phone, agency) for whoever books on the
   party's behalf. See DATABASE_DESIGN §2 (`groups` booking-agent fields).
3. **Nickname table — YES**, seed from ours and grow it as staff confirm merges.

## Validation — v2 run with these rules applied (2,706 rows)
| Metric | v1 (email/phone only) | v2 (rules applied) |
|---|---|---|
| Master persons | 2,481 | **1,748** |
| People spanning 2+ source types | 90 | **548** |
| Name-only auto-attached (unique match) | — | **824** |
| Ambiguous → review queue | — | **41** |
| Bookings linked to their group (name+arrival) | — | **135 / 139** |
| Shared/agent emails caught (guardrail) | 16 | **58** |
| Groups given a booking-agent contact | — | **53** |
| Example: the Younger master record | 4 rows | **21 rows** |

The rules hold on real data: one person's 15 inquiries + 2 bookings + 3 leads + guest profile
collapse into a single record, agent inboxes no longer fuse different guests, and nearly every
booking links to its group. The 41 ambiguous + 58 agent-email cases are the standing **review queue**.

## Next step
Port this engine to the Laravel API (`scripts/match-prototype.js` is the reference), and keep the v2
output as the regression fixture — especially the Younger assembly, the agent-email splits, and the
booking→group links.
