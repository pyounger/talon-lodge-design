# Master-Record Management — the spine of the system

**This is the most critical element of the platform.** Everything else attaches to it.
Visual companion: [`record-management.html`](record-management.html). Data model:
[`DATABASE_DESIGN.md`](DATABASE_DESIGN.md) (§2 people model).

## The principle
The system keeps **exactly one master `Person` record per human being**. A person is not
re-created each time they appear — every arrival is matched against who is already known.
A person's role, group, and trip are things that happen *to* a person over time; the person
itself is permanent. **History only accumulates — it is never overwritten.**

**Recognition photo.** The master record carries a person photo (`persons.photo_url`, object storage)
used across reports so staff can greet guests by sight. For a **repeat** guest it is imported from
existing data; for a **new** guest it is captured at the lodge and added to the record.

---

## The three intake channels
Every channel produces a *candidate* that runs through the **same** matching engine
(`resolveGuestForCandidate()`). None of them create a person directly.

### 1. Website contact form
- Sites: talonlodge.com, alaskaluxurylodge.com, magnusadventures.com.
- Lets a person ask basic questions. Fields: name, email, phone, message.
- → matched → links to an existing person or creates a new record (usually an inquiry/lead).

### 2. Reservation request & booking
- The person who books **becomes the Group Lead** for that reservation.
- On confirmation the system creates: the person (via matching), a **Group** (lead = this person),
  a **Trip** (the dated booking), and a group membership with **role = Lead**.
- A **scheduled communication** then goes to the lead after confirmation, asking for the guest list.

### 3. Guest list (submitted by the Group Lead)
- The lead lists the travelers. Per traveler: name, email, "past guest?".
- Each entry runs through matching → links to an existing person or creates a new record, then is
  **attached to the group** with **role = Member**, and each guest receives their **own portal invite**
  to manage their own information.

---

## The matching engine (how one record is maintained)
| Tier | Signal | Action |
|---|---|---|
| 1 | Exact email match (normalized) | **Auto-link** to the existing person |
| 2 | Exact phone + nickname-equivalent name (Bob = Robert) | **Auto-link** |
| 3 | Nickname-equiv name + same last name, **no** email/phone | **Flag → Merge Review Queue** (a human decides) |
| — | No signal | **Create a new master record** |

- Nickname equivalence uses the shared nickname table (resolves "Phil / Philip", etc.).
- **Name-only auto-attach:** an inquiry/booking with no contact that matches **exactly one** known
  person attaches to them automatically; ambiguous names go to review. (Validated on real data — see
  [`MATCHING_RULES.md`](MATCHING_RULES.md).)
- **Booking agents:** a shared inbox that books for several guests is stored as the **Group's
  booking-agent contact**, never merged into a guest's record.
- **Merge/undo safety:** every merge — automatic (Tier 1/2) or human-confirmed (Tier 3) — stores
  the losing and surviving pre-merge states and the exact records it re-pointed, so it can be
  **undone precisely**. Merges are the only action that rewrites data across records, so they are the
  only action with full reversibility. (See `db/migrations/0008` / DATABASE_DESIGN §4.)

---

## Role over time — one person, many groups
Role lives on the **membership**, not the person:

```
person ──< group_person (role: lead | member) >── group ── trip (dated)
```
A person's full history = **all** their `group_person` rows, joined through `group` → `trip`.
Opening a person shows every group they were in, in what role, on which trip, plus the
accommodations, boats, and activities from each.

### Worked example — Phil Younger
- **2019** — added via the **Marshall Group** lead's guest list → `group_person(role=member)` on the
  Marshall group's 2019 trip. Got his own portal invite; managed his own profile/flights/activities.
- **2025** — booked his own reservation → matching hits his 2019 **email (Tier 1)** → **auto-links to
  the same person** (no duplicate) → new **Younger Group**, `group_person(role=lead)`, 2025 trip → he
  then submits his own guest list (which creates/links his party the same way).

Result: opening **Phil Younger** shows *guest of the Marshall group in 2019* **and** *lead of his own
group in 2025* — same record, both roles, full history. A guest becoming a lead needs no special
handling; it is just another membership with a different role.
