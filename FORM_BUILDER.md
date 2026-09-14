# Form Builder — admin-configurable intake forms

Letting an admin decide what a public form asks, without a developer and without a deploy.
Prototype: [`form-builder.html`](form-builder.html). The form it configures:
[`contact-form.html`](contact-form.html) · contract: [`INQUIRY_INTAKE.md`](INQUIRY_INTAKE.md).

**The headline: almost none of this is new.** `DB_SCHEMA.md` §0 already specifies a
meta-schema — `field_definitions` + `field_groups`, *"structure as data… with no
migrations"* — and `DEVELOPER_TASKS.md` §3 already carries the build task
(*"Meta-schema engine: read `field_definitions` to drive validation + dynamic forms"*).
The decision is marked **locked**. This document points that existing engine at intake and
adds the one thing it is missing.

---

## The distinction that matters

"Add or remove an activity from the form" sounds like form building. It isn't, and building
it that way is the mistake to avoid.

An activity is already a record. From the live catalog (`activities-admin.html`):

```
{ id, name, icon, desc, url, priceText, priceFrom, priceTo, unit,
  minPeople, season, availability, times, status, sort, photos }
```

If the builder asks an admin to re-enter activity names as form options, there are now two
lists of activities that must agree. They will drift — someone renames *ATV Kruzof Island
Tour* in the catalog and the enquiry form keeps the old name for a season.

Worse, retyping throws away data the form could be using. Three real examples from today's
catalog:

| Activity | Catalog says | What a catalog-driven form can do |
|---|---|---|
| Freshwater Fishing — By ATV | `status: seasonal`, `season: "Aug & Sept"` | Hide it when the enquiry is for June |
| Whale & Wildlife Viewing | `minPeople: 4` | Flag it when the party is 2 |
| Additional Saltwater Sportfishing | `availability: arrival_departure` | Note that it attaches to travel days |

None of that is possible if the list is hand-maintained form config. So:

> **Catalog content is never retyped into form config. The form reads the catalog; the admin
> controls visibility.**

---

## Three layers

### 1. Locked core — not configurable

Name, email, dates, guest count, message. Admins may reorder and relabel. They may **not**
remove these or make them optional.

This is the layer that needs defending, because every form builder drifts toward letting
admins switch anything off, and the fields that must never be optional are exactly the ones
protecting data quality.

**Email specifically.** `MATCHING_RULES.md` found **1,115 name-only persons with no email or
phone — *"almost all inquiries — unmatchable by contact"*** across the real 2026 exports.
That pile exists *because* intake was loose. A builder that lets someone uncheck "required"
on email rebuilds it with a nicer UI. Email is also what makes the auto-reply possible at
all.

Server-set fields — `property_id`, `website`, `form_name`, `person_id` — are not shown to
admins in any form. They are not fields; they are provenance.

### 2. Catalog-derived blocks — visibility only

Activities, packages, properties. The admin sees the real catalog and toggles what appears
on each property's form. Labels, descriptions, minimums and seasons come from the record.

Storage needs **no new table**. `DATABASE_DESIGN.md` already models activities as `assets`
(*"asset_types define what a property offers — room, boat, guide, massage, activity…"*) with
a governed `properties` JSON bag. Visibility is one more governed key:

```
assets.properties.offer_on_enquiry_form : boolean   (default true)
```

Because assets belong to a property, per-property variation falls out for free — Talon and
Magnus can offer different sets with no extra modelling.

### 3. Custom questions — genuine form building

"How did you hear about us", "purpose of travel", "times to Alaska before". These are real
`field_definitions` rows and the existing engine already handles them: `label`, `data_type`,
`input_type`, `required`, `sort_order`, `options`, `validation`, `help_text`, `reportable`.

`field_definitions.property_id` is already `null = platform-wide default, set = that
property's custom field`, so one property can add a question the others never see.

---

## Schema changes required

Two, both small:

1. **`field_definitions.target`** currently accepts `asset | trip_profile | assignment |
   person`. Add **`inquiry`**. This is the only change to the meta-schema itself.
2. **`inquiries.details`** JSON, governed by those definitions — already proposed in
   INQUIRY_INTAKE.md as the place the non-core answers land.

Plus one seed row: a boolean field definition for `offer_on_enquiry_form` against the
activity asset type.

That is the whole schema cost. No form-definition tables, no form-version tables, no
per-field storage table.

---

## Guardrails

1. **The core cannot be removed or made optional.** Enforce server-side, not only in the
   admin UI — the endpoint validates against the core regardless of configuration.
2. **Visibility is not deletion.** Hiding an activity from a form never touches the activity.
   An enquiry that already referenced it still renders correctly.
3. **Changes are versioned and attributed.** `created_by` / `updated_by` are already
   repo-wide conventions (DEVELOPER_TASKS §0). A form that silently changed shape is a
   support problem when an agent asks why an enquiry lacks a field.
4. **Reportable is a deliberate flag, not a default.** `field_definitions.reportable`
   already exists. Custom questions nobody reports on are just clutter that survives for
   years.
5. **A preview before publish.** The admin sees the real form, per property, before it goes
   live. The prototype shows this side by side.

---

## What this buys

The change Phil asked for on 14 Sep — drop the fishing framing, consolidate four fishing
activities into two, reorder the list to lead with wildlife and spa — was a code edit, a
rebuild and a redeploy. Under this design it is an admin toggling visibility and editing two
labels, live, in about a minute.

The same engine then drives the brochure request, the reservation request, and the guest
portal's profile forms. Intake is simply the first place it pays off.

---

## Open questions

1. **Who may edit?** A property manager, or platform admin only? Custom questions change what
   is captured forever; visibility toggles are harmless. They may deserve different
   permissions.
2. **Per-form or per-property?** A property could run a contact form *and* a brochure request
   with different activity sets. `form_name` already distinguishes them — is that granularity
   wanted, or is per-property enough?
3. **Ordering.** Does the admin set activity order on the form, or does it follow the
   catalog's existing `sort`? Following `sort` is one less thing to maintain.
4. **Retiring a question.** When a custom question is removed, its answers stay in
   `inquiries.details` on old rows. Hide from reports, or keep visible as historical?

---

## Related

`DB_SCHEMA.md` §0 (meta-schema) · `DATABASE_DESIGN.md` (assets + governed JSON) ·
`DEVELOPER_TASKS.md` §3 · `INQUIRY_INTAKE.md` · [`form-builder.html`](form-builder.html)
