# Developer Tasks — from approved design to working system

Assumes the revised data model (DB_SCHEMA.md, incl. §0 meta-schema) is approved. Grouped by owner:
**[DEV]** = only the developer can do it (infra, access, credentials, decisions, deploy);
**[GEN→DEV]** = Claude can generate it for the developer to review + run. Ordered roughly by dependency.

## 0. Decisions to lock (quick) — [DEV]
- [ ] Approve the revised schema (properties · unified assets · assignments · meta-schema · group 1:1 trip).
- [ ] **Meta-schema value storage:** JSON governed by `field_definitions` (recommended) vs. a normalized `field_values` (EAV) table.
- [ ] Confirm conventions already agreed: `active` soft-delete (no hard deletes), `created_by`/`updated_by`, FK-on/cascade-off, bigint `id` + `ulid`.

## 1. Infrastructure & access — [DEV]
- [ ] **Aurora MySQL 8**: cluster, `talon` database, two roles (`migrator` = DDL, `app_user` = CRUD), parameter group, Multi-AZ, backups + PITR.
- [ ] **App host**: ready the AL2023 box — PHP 8.2+, Composer, Node 20/22 LTS, nginx (or existing stack), pm2/systemd.
- [ ] **S3 bucket**: private, **encrypted at rest**, IAM scoped to the bucket, CORS for the app origin, presigned-URL access.
- [ ] **Secrets Manager**: DB creds, S3 keys, `ANTHROPIC_API_KEY` (server-side only), SES creds, session secret.
- [ ] **SES**: verify sending domain (`talonlodge.com`) + DKIM/SPF; leave sandbox before go-live (needed for guest magic-link + comms).
- [ ] **GitHub**: add collaborators to `talon-lodge-api` / `talon-lodge-ui`; set branch protection.
- [ ] **DNS + TLS**: `platform.talonlodge.com` (and portal subdomain); ACM or certbot.

## 2. Legacy data to provide — [DEV]  (unblocks the final merge; drop in `references/`, gitignored)
- [ ] Exports **and** schemas of the three source systems: **reservation**, **profile/activity**, **survey (SurveyMonkey)**.
- [ ] Where existing **guest photos** live (folder / DB field / URL) → maps to `persons.photo_url` for repeat guests.
- [ ] Any known field mappings, ID schemes, and data-quality quirks.

## 3. Backend build — [GEN→DEV]  (Claude generates; developer reviews + runs)
- [ ] Scaffold Laravel around the domain code (SCAFFOLD.md); `.env` → Aurora MySQL; `migrate` + `seed` + `test`.
- [ ] **Regenerate migrations + models** to the approved revised schema (properties, assets, assignments, meta-schema, audit/active, group 1:1).
- [ ] **Meta-schema engine**: read `field_definitions` to drive validation + dynamic forms; generate/index reportable JSON keys.
- [ ] **Matching**: finish the engine in Laravel (port done) + the **bulk CSV importer** command + the **MergeService** (merge + undo, per MERGE_RULES IF/THEN) + tests.
- [ ] **Auth**: staff accounts + roles/permissions; **guest magic-link** for the portal.
- [ ] **Availability engine** + booking locks; the **embeddable availability widget** for the 3 sites.
- [ ] **Communications**: pre-arrival (portal magic-link), daily agendas, post-stay survey invites — via SES.
- [ ] **Payments** (Stripe): deposits, invoices, webhooks.
- [ ] **Reports** (use the recognition photo, stay history, survey score, etc.).

## 4. Frontend build (Angular / Daxa) — [DEV] scaffold, [GEN→DEV] screens
- [ ] Scaffold `talon-lodge-ui` from the licensed Daxa source; **pin versions + commit a lockfile** (UI_MAPPING gotcha).
- [ ] Build admin + Guest Portal screens per UI_MAPPING — **theme framework only, no custom CSS**; forms driven by the meta-schema.

## 5. Final data migration (the hard phase) — [GEN→DEV] + [DEV]
- [ ] Run matching/merge over the three systems into the master DB; work the review queue; import guest photos.

## 6. Ops — [DEV]
- [ ] CI (lint + tests), deploy pipeline (SFTP/pm2 or containers), backup verification, CloudWatch logs + alarms.

---
**Critical path:** §0 decisions → §1 DB + host + secrets → scaffold + regenerated migrations → auth → matching/merge → intake + portal → payments/availability → §2/§5 legacy merge. The matching/merge engine is already designed, validated on real data, and (for matching) coded — it's the lowest-risk core.
