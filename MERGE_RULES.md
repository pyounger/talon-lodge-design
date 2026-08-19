# Merge & Master-Record Rules

The **only** operation that rewrites data across many tables at once, so it is the one action
built for full reversibility (SPEC §2.4). This doc details: when merges happen, how the master
record's ID is managed, exactly what a merge does, and how a merge is reversed.

Companions: [`MATCHING_RULES.md`](MATCHING_RULES.md) (how duplicates are detected),
[`RECORD_MANAGEMENT.md`](RECORD_MANAGEMENT.md) (the intake process), `DB_SCHEMA.md §D/§G`.

> **Link vs merge.** Attaching an intake record to a person (`person_id` set by the matching
> engine) is *linking* — routine, not a merge. A **merge** combines **two existing `person`
> records** that turn out to be the same human. This doc is about merges.

---

## 1. When a merge happens
- **Auto (Tier 1/2).** During intake or bulk import, a strong signal (exact email, or phone +
  nickname-equivalent name) shows that two *existing* person records are the same human — e.g. two
  records were created separately before a connecting email/phone appeared. The engine merges them.
- **Manual (Tier 3 confirmed).** Staff act on a `merge_review_queue` entry and choose
  **Merge into [survivor]** (or **Not a match**, which closes the entry with no merge).
- **Never merged (→ stay in review).** Shared/agent emails (one inbox, many guests), ambiguous
  common names, and any below-threshold guess. These never auto-merge.

## 2. Choosing the survivor (which record keeps the master ID)
Default precedence (used for auto-merge, and as the suggested survivor in manual review):
1. **Most linked history** — trips/reservations/profiles/surveys attached.
2. else **earliest `first_seen_at` / `created_at`** — the longest-known record.
3. else **most complete** — fewest null core fields.
4. else **lower `id`** — stable tie-break.

For a **manual** merge, staff explicitly pick the survivor ("merge INTO this one"); the rule above
only pre-selects the default. The other record becomes the **loser** (the duplicate folded in).

## 3. Master-record ID management  (this is the guarantee external systems rely on)
- **`id` (bigint, internal):** never exposed, never changes. The **survivor keeps its `id`.**
- **`ulid` (public key):** the **survivor keeps its `ulid`** — it is permanent and is what portal
  magic-links, invoices, and URLs reference.
- **Loser's `ulid` → `person_ulid_redirects`** (old ulid → survivor). Any lookup by the loser's old
  ulid resolves to the survivor, so **prior links keep working** after a merge.
- A merge only ever **removes a duplicate** — the survivor is **never re-IDed**. Therefore a
  person's master ULID is **stable for life**, through any number of merges.

## 4. What a merge does (one DB transaction)
**Field reconciliation on the survivor:**
- **Core fields:** survivor's non-null values win; loser's non-null values **gap-fill** the
  survivor's nulls. Any *differing* loser value is preserved (a differing name → `person_name_aliases`;
  others captured in the snapshot).
- **Emails / phones:** union both onto the survivor (dedupe by normalized value); survivor's primary
  stays primary, the loser's become secondary.
- **Aliases:** union; the loser's name is added as an alias if different.

**Re-point every record that referenced the loser → survivor** (the exact ids are recorded):
`group_persons` · `groups.lead_person_id` · `trip_profiles` · `assignments` (person; incl. any
guide reference in `details`) · `inquiries` · `leads` · `reservation_requests` · `brochure_requests` ·
`guest_list_entries` · `survey_scores` · `survey_invitations` · `invoices.bill_to_person_id` ·
`stay_media` · `merge_review_queue`.

**Dedupe on re-point** where a unique constraint exists — e.g. both were members of the same group
(`group_person` unique(group,person)) → keep one, preferring role `lead`; duplicate normalized email
→ keep one. Rows removed by dedupe are **captured in the snapshot** so undo can restore them.

**Finalize:** soft-delete the loser `person` row (`deleted_at`, **not** hard-deleted — undo needs it),
add the loser-ulid redirect, recompute the survivor's cached rollups, and write the audit record (§5).

## 5. The audit record — `merge_history` (one row per merge, on the survivor; never deletable)
- `kind` (auto | manual), `survivor_person_id`, `loser_person_id`, `performed_by`
- `survivor_snapshot` JSON — the survivor's **exact pre-merge** core state (so undo restores
  precisely, not approximately)
- `loser_snapshot` JSON — the loser's exact pre-merge state **including its child rows and any rows
  removed by dedupe**
- `repointed_records` JSON — `[{table, id, from_person_id, to_person_id}]`: the **exact** records moved
- `review_queue_id` (manual), `created_at`, `undone_at` (null = in effect), `undone_by`

## 6. Reversing a merge (undo)
**Undo rule:** only the **most recent, not-yet-undone** merge on a given survivor may be undone. If
merges have stacked, unwind them newest-first. This prevents inconsistent partial undos.

**Steps (one transaction):**
1. **Validate** — confirm this `merge_history` row is the latest with `undone_at IS NULL` for that survivor.
2. **Restore the loser** — clear its `deleted_at` (reuses its original `id` and `ulid`).
3. **Move back exactly the `repointed_records`** to the loser — *only* those ids.
4. **Recreate** any rows removed by dedupe during the merge, from `loser_snapshot`.
5. **Restore the survivor's core fields** to `survivor_snapshot` (undoes gap-fill precisely).
6. **Remove loser-contributed** emails/phones/aliases from the survivor.
7. **Delete the loser's `person_ulid_redirects`** row.
8. **Manual merges:** reset the linked `merge_review_queue` entry to `pending`.
9. **Recompute rollups** for both records.
10. **Stamp** `undone_at` + `undone_by`. The undo is itself audited (nothing is hard-deleted).

**Not reverted:** any record that began pointing at the survivor *after* the merge (unrelated new
activity) stays with the survivor — because only the recorded ids move back. This is the whole reason
the exact id list is stored, rather than "everything currently pointing at the survivor."

## 7. Guardrails & edge cases
- No auto-merge on shared/agent emails or ambiguous names — those go to review.
- **Post-merge email degradation:** if a survivor's email *later* turns out to be a shared/agent inbox
  (used by ≥2 people), it is **demoted** — moved to booking-agent context on the relevant group — and
  **does NOT trigger a retroactive unmerge**. A completed merge is only ever reversed by an explicit
  undo (§6). This preserves merge integrity.
- Can't undo a merge that isn't the latest on that survivor — unwind in order.
- **Concurrency:** lock the survivor + loser rows for the duration; the whole merge/undo is one
  transaction that rolls back on any failure.
- **Chained merges:** merges are pairwise (loser → survivor); a survivor can later be a loser in a
  further merge. Undo order is enforced per record.
- **Hard-deleting a person** is a separate action and is blocked while `merge_history` references it
  (the audit trail is preserved).

## If/Then rules (implementation logic)

### A. Should we merge? (detection)
- **IF** a candidate's normalized email exactly matches an existing person **AND** that email maps to only **one** person → **THEN** auto-link/merge *(Tier 1)*.
- **IF** an email maps to **≥2 distinct people** → **THEN** it's a shared/agent inbox → **do NOT merge on it**; store it on the group's booking-agent fields; send to review.
- **IF** a normalized phone matches **AND** the names are nickname-equivalent → **THEN** auto-merge *(Tier 2)*.
- **IF** a phone matches **BUT** names are **not** nickname-equivalent → **THEN** do **not** merge *(household phone)*.
- **IF** only the name matches (nickname + last), no email/phone → **THEN** do **not** auto-merge; **IF** exactly one contactful person has that name → auto-attach the record; **IF** >1 → review; **IF** 0 → new record.
- **IF** the checks above identify two **existing** person records as the same human → **THEN** run a merge (loser → survivor).

### B. Which record survives? (keeps the master id + ulid)
- **IF** manual merge → **THEN** survivor = the record staff picked.
- **ELSE IF** one record has more linked history → **THEN** it survives.
- **ELSE IF** one has an earlier `first_seen_at`/`created_at` → **THEN** the older survives.
- **ELSE IF** one has more complete core fields → **THEN** the more complete survives.
- **ELSE** → **THEN** the lower `id` survives.

### C. Folding fields
- **IF** a survivor field is null **AND** the loser's is set → **THEN** copy the loser's value (gap-fill).
- **IF** both are set and differ → **THEN** keep the survivor's; **IF** it's the name → add the loser's to `person_name_aliases`; **ELSE** record the differing value in `loser_snapshot`.
- **IF** the survivor has no photo **AND** the loser has one → **THEN** the survivor takes the loser's photo.
- **IF** the loser has an email/phone the survivor lacks → **THEN** add it to the survivor as secondary (dedupe by normalized value).
- **IF** a loser email/phone duplicates the survivor's → **THEN** drop it (record in `loser_snapshot`).

### D. Re-pointing & dedupe
- **FOR each** record referencing the loser → **THEN** set its person FK to the survivor and record `{table, id, from, to}` in `repointed_records`.
- **IF** re-pointing would break a unique constraint (both in the same `group_person`; duplicate normalized email) → **THEN** keep one row (prefer role `lead`, prefer the survivor's primary), remove the duplicate, and record it in `loser_snapshot`.

### E. Finalize (all in one transaction)
- **THEN** soft-delete the loser (`deleted_at`) — **never** hard-delete.
- **THEN** insert `person_ulid_redirects` (loser ulid → survivor).
- **THEN** recompute the survivor's rollups.
- **THEN** write `merge_history` (kind, both snapshots, `repointed_records`, `performed_by`).
- **IF** manual → **THEN** set the review-queue entry `status='merged'` (`resolved_by`/`resolved_at`).
- **IF** any step fails → **THEN** roll back the whole transaction.

### F. Can we undo? (reversal eligibility)
- **IF** this `merge_history` row is **not** the most recent with `undone_at IS NULL` for that survivor → **THEN** block (unwind newer merges first).
- **IF** `undone_at` is already set → **THEN** block (already undone).
- **ELSE** → **THEN** proceed.

### G. Undo actions (all in one transaction)
- **THEN** restore the loser (clear `deleted_at`; reuse its original `id` + `ulid`).
- **FOR each** entry in `repointed_records` → **THEN** move that record's person FK back to the loser — **only** those ids.
- **IF** a row was removed by dedupe during the merge → **THEN** recreate it from `loser_snapshot`.
- **THEN** restore the survivor's core fields from `survivor_snapshot` (undo gap-fill exactly).
- **THEN** remove loser-contributed emails/phones/aliases from the survivor.
- **THEN** delete the loser's `person_ulid_redirects` row.
- **IF** the merge was manual → **THEN** reset the review-queue entry to `pending` (clear `resolved_by`/`resolved_at`).
- **THEN** recompute rollups for both records; stamp `undone_at` + `undone_by`.
- **IF** a record started pointing at the survivor **after** the merge (not in `repointed_records`) → **THEN** leave it on the survivor (do **not** move it back).
- **IF** any step fails → **THEN** roll back; nothing is hard-deleted.
- **IF** someone tries to hard-delete a person referenced by `merge_history` → **THEN** block (preserve the audit trail).

## Schema touchpoints
`persons.deleted_at` · `merge_review_queue` (+ `resolved_by`) · `merge_history`
(+ `loser_person_id`, `performed_by`, `undone_by`) · **`person_ulid_redirects`**. See DB_SCHEMA §G.
