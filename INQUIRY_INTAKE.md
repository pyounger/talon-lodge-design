# Enquiry Intake — contact form → `inquiries`

The contact form that sits on **talonlodge.com**, **alaskaluxurylodge.com** and
**magnusadventures.com**. One form, one endpoint, one table. Prototype:
[`contact-form.html`](contact-form.html).

This is the contract for the developer building the endpoint. It proposes; it does not
describe built behaviour. Open questions are listed at the end.

---

## Why this document exists

Enquiries are the front door of the Person record. Everything downstream — matching, the
golden record, stay history, the survey score — starts from whatever this form captures.
Get it wrong and it is not a form bug, it is a data-quality problem that compounds for
years.

The matching run over the real 2026 exports (MATCHING_RULES.md) is the evidence:

| Metric | Value |
|---|---|
| Inquiry rows | 1,000 |
| Name-only persons, no email or phone | **1,115 — "almost all inquiries — unmatchable by contact"** |
| Name-only records matching a contactful person by name | 859 |

The existing enquiry forms are the single largest source of unmatchable records in the
dataset. MATCHING_RULES.md §8 even carries a hygiene rule to scrape an email or phone out
of the free-text comment to rescue some of them.

**So: email is required.** It is also required for the auto-reply to exist at all. This one
constraint is the main thing this document is defending.

---

## Endpoint

```
POST /inquiries
Content-Type: application/json
```

Public, unauthenticated, CORS-restricted to the three site origins.

### Request body

```jsonc
{
  "name":    "Margaret Ellison",
  "email":   "m.ellison@example.com",   // required
  "phone":   "(206) 555-0148",          // optional
  "message": "Celebrating my father's 70th…",
  "details": {
    "arrival_date":        "2027-07-11",
    "departure_date":      "2027-07-16",
    "nights":              5,
    "date_flexibility":    "exact",      // exact | few_days | month | unsure
    "season_year":         "2027",
    "months_of_interest":  ["July"],
    "num_fishing_guests":     4,
    "num_non_fishing_guests": 2,
    "party_size":             6,
    "children":            true,
    "child_ages":          "9, 12, 14",
    "interests":           ["Saltwater sportfishing", "Whale & wildlife viewing"],
    "enquiring_as":        "self",       // self | group | agent
    "agency_name":         null,
    "agency_email":        null,
    "times_to_alaska_before": "1",
    "how_heard":           "referral",
    "opt_in_offers":       false
  }
}
```

### Set by the server, never accepted from the browser

| Field | Source |
|---|---|
| `property_id` | The site key the request arrived on |
| `website` | Origin host |
| `form_name` | Which form (`contact-us`) |
| `person_id` | Left null; the matching engine fills it |
| `received_at`, source IP | Request metadata |

A browser that can set its own `property_id` can route an enquiry to the wrong lodge's
queue. Derive it from the origin.

---

## Mapping to the schema

Everything lands in **`inquiries`** (DB_SCHEMA §F). No new table.

| Body field | Column | Note |
|---|---|---|
| `name` | `name` | |
| `email` | `email` | **Required** — see above |
| `phone` | `phone` | |
| `message` | `message` | |
| — | `property_id`, `website`, `form_name` | Server-set; all three already exist in §F |
| — | `person_id` | Null on write |
| `details` | `details` JSON **(proposed)** | Governed by `field_definitions`, the way `assets.properties` and `trip_profiles.details` already work |

`inquiries` has no `details` column today. Two options:

1. **Add `details` JSON**, governed by the meta-schema. Consistent with the hybrid flexible
   model in DATABASE_DESIGN.md, and lets each property add its own questions without a
   migration. *Recommended.*
2. **Promote the common fields to real columns** — `arrival_date`, `departure_date`,
   `num_fishing_guests`, `num_non_fishing_guests`, `party_size` — and put only the tail in
   JSON. Every enquiry has these, they are the ones reports will group by, and
   `brochure_requests` already stores `num_fishing/non_fishing_guests` as columns.

A reasonable answer is both: promote the five, JSON for the rest.

---

## The two messages

### 1. Guest auto-reply — immediate

Sent on successful write, before any human sees it. Speed is the point: a guest who hears
nothing for an hour enquires at three other lodges.

- **From** the property, **reply-to the assigned agent** — never a no-reply address. A
  reply must land on a person and thread onto the same enquiry.
- **Recaps their own answers** — lodge, dates, party split, interests. A generic
  acknowledgement tells them nothing and reads as automated.
- **Suggests packages from their interests** (see the prototype for the mapping —
  saltwater + viewing → Alaska Adventure Combo, and so on).
- **Names the agent and gives a timeframe.** "Dana will come back to you within one
  business day" is a commitment; "we'll be in touch" is not.
- **States that nothing is held or charged.** Removes the main reason people hesitate.
- Honours `persons.do_not_email`. The auto-reply is transactional, not marketing —
  `opt_in_offers` governs the newsletter, not this.

### 2. Agent notification — immediate

- **Routed by `property_id`** to that property's assigned agents; falls back to the
  property's `contact_email` if none is on duty.
- **A record in the system with a claim action, not only an email.** An enquiry that lives
  only in one person's inbox gets lost when they are on the water.
- **Escalates when unclaimed** — 2 working hours to the property manager, 8 to the group
  inbox.
- **Flags computed on arrival**, so priority is visible before opening: party size, peak
  weeks (June/July), repeat-guest match, travel-agent enquiry, buyout interest.
- **Shows the matching result.** If the email resolves to an existing person, the agent
  sees stay history and last survey score before replying. This is the payoff for the
  whole matching engine and it shows up first, here.

---

## Three things the form does deliberately

**Anglers and non-anglers counted separately.** Not a single "number of guests". Boats and
pricing are assigned by who is fishing, and `brochure_requests` already splits them.

**"Not sure yet" is a first-class answer on dates.** Many enquirers have no dates — that is
why they are enquiring. Forcing a date produces a fictional one. Choosing it reveals a
month picker and a note about when kings and silvers run.

**"Enquiring as" — self, group organiser, or travel agent.** The matching run found 16
shared-email-across-different-surnames cases flagged as an *over-merge trap*. Capturing
agent status at intake keeps the agent's details on the group (`groups.booking_agent_*`)
instead of fusing unrelated guests onto one email.

---

## Open questions for the developer

1. **`details` JSON, promoted columns, or both?** (See the mapping section.)
2. **Spam protection.** Three public endpoints need it. Honeypot plus rate limiting, or a
   CAPTCHA? A CAPTCHA costs conversions on a low-volume, high-value form — worth avoiding
   if rate limiting will do.
3. **Bluff House.** MODULE_ROADMAP lists four properties (Talon, Bluff House, Alaska
   Luxury, Magnus) across three websites. Is Bluff House a `property` with its own queue,
   selectable on the Talon form, or accommodation within Talon? The prototype assumes the
   latter.
4. **Embed mechanism.** MODULE_ROADMAP already plans an embeddable availability widget for
   these same three sites. This form should use whatever that lands on rather than
   inventing a second embed.
5. **Agent assignment.** Is there an agents-per-property table and a duty roster, or is
   routing just the property `contact_email` for now?

---

## Related

`DB_SCHEMA.md` §F · `DATABASE_DESIGN.md` · `MATCHING_RULES.md` · `MODULE_ROADMAP.md`
Phase 2 · [`contact-form.html`](contact-form.html)
