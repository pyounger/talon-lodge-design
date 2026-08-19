# Server Setup Guide — Talon Lodge Platform

**Audience:** the developer standing up the environment(s).
**Goal:** a correct, secure, reproducible deployment of the platform described in
[`SPEC.md`](../SPEC.md), on the architecture recommended in SPEC §8.

This is a living document. Anything marked **DECISION** needs Phil's sign-off before
you provision it — do not guess (see §10).

---

## 0. TL;DR checklist

- [ ] AWS account, region, and VPC chosen (§1)
- [ ] Aurora PostgreSQL cluster provisioned, `pg_trgm` / `pgcrypto` / `citext` enabled (§2)
- [ ] App DB + two roles (`migrator`, `app_user`) created (§2.4)
- [ ] Migrations applied (`scripts/migrate.sh`) + seed loaded (`scripts/seed.sh`) (§2.5)
- [ ] S3 (or R2) media bucket, private, with presigned-URL access (§3)
- [ ] Backend host ready (EC2 + pm2, or ECS Fargate) with `.env` from Secrets Manager (§4)
- [ ] Reverse proxy + TLS (nginx+certbot or ALB+ACM) (§5)
- [ ] Security groups locked down: only the app can reach the DB (§6)
- [ ] SES verified sending domain for guest magic-link email (§7)
- [ ] Backups/PITR confirmed, CloudWatch logs/alarms wired (§8)
- [ ] CI/CD deploy path working end to end (§9)

---

## 1. Architecture

```
                    ┌──────────────────────────────────────────┐
   Guests / Staff   │                 AWS VPC                    │
        │           │                                            │
        ▼           │   public subnet          private subnet    │
   ┌─────────┐      │  ┌───────────────┐      ┌───────────────┐  │
   │  CDN /   │─────┼─▶│ Reverse proxy │─────▶│  Backend API   │  │
   │CloudFront│     │  │ (nginx / ALB) │      │  (Node + TS)   │  │
   │ (static  │     │  │  TLS term.    │      │  pm2 or Fargate│  │
   │  React)  │     │  └───────────────┘      └───────┬───────┘  │
   └─────────┘      │                                 │          │
                    │                    ┌────────────┴───────┐  │
                    │                    ▼                    ▼  │
                    │           ┌─────────────────┐  ┌────────────────┐
                    │           │ Aurora PostgreSQL│  │ S3 media bucket │
                    │           │ (pg_trgm, Multi-AZ)  │ (private)      │
                    │           └─────────────────┘  └────────────────┘
                    └──────────────────────────────────────────┘
         External: Anthropic API (server→server only) · SES (magic-link email)
```

**Components**

| Component | Choice | Why |
|---|---|---|
| Database | **Aurora PostgreSQL 15.x/16.x** | Relational fit + `pg_trgm` for the guest-matching engine |
| Backend | **Node 20 LTS + TypeScript** | One language with the React frontend; matches existing pm2/EC2 ops |
| Frontend | **React + TypeScript**, static build | Served from CloudFront/S3 or by nginx |
| Object storage | **S3** (or Cloudflare R2) | Real photo/file storage — no base64 data URLs |
| AI | Anthropic API from the **backend only** | The API key must never reach the browser |
| Email | **SES** | Guest Portal magic-link auth |
| Secrets | **SSM Parameter Store / Secrets Manager** | No secrets in code, env files, or the repo |

**Two deployment shapes — DECISION (§10):**
- **A. EC2 + pm2 (recommended to start).** One AL2023 instance runs the Node service under
  pm2 behind nginx. Lowest operational overhead and matches the existing Talon deploy
  pattern. Scale vertically first.
- **B. ECS Fargate + ALB.** Containerized, autoscaling, no host to patch. More moving parts.
  Worth it once traffic or team size justifies it.

This guide gives concrete steps for **A**, with notes for **B**.

---

## 2. Database — Aurora PostgreSQL

### 2.1 Provision
- Engine: **Aurora PostgreSQL**, latest 15.x or 16.x.
- Topology: **Multi-AZ** (a writer + at least one reader) for production.
- Placement: **private subnets only**. No public accessibility.
- Instance class: start `db.r6g.large` (prod) / `db.t4g.medium` (staging); adjust later.
- Storage: Aurora auto-scales; enable **encryption at rest** (KMS).
- Note the **cluster writer endpoint** (`...cluster-xxxx.<region>.rds.amazonaws.com`) and
  the **reader endpoint** — the app uses the writer; reporting/read-replicas can use the reader.

### 2.2 Parameter group
- Create a custom cluster parameter group.
- Ensure `rds.force_ssl = 1` (require TLS).
- No special tuning needed for `pg_trgm` beyond the extension itself.

### 2.3 Extensions
The three extensions the schema needs are all on the RDS/Aurora allowlist and are created
by migration `0001_extensions.sql`, run as the master (or `migrator`) user:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pg_trgm;    -- fuzzy guest matching
CREATE EXTENSION IF NOT EXISTS citext;     -- case-insensitive email/slug
```
Nothing to pre-install — RDS ships them; `CREATE EXTENSION` is enough.

### 2.4 Database and roles (least privilege)
Connect as the master user and create the app database and two roles:

```sql
CREATE DATABASE lodge;
\connect lodge

-- Schema owner / migrations. Used ONLY by scripts/migrate.sh in deploys.
CREATE ROLE migrator LOGIN PASSWORD 'CHANGE_ME';
GRANT ALL PRIVILEGES ON DATABASE lodge TO migrator;

-- Runtime app role: CRUD only, no DDL.
CREATE ROLE app_user LOGIN PASSWORD 'CHANGE_ME';
GRANT CONNECT ON DATABASE lodge TO app_user;
```

After the first migration run (which creates the tables as `migrator`), grant runtime
privileges and make them apply to future tables too:

```sql
\connect lodge
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO app_user;
```

- `DATABASE_ADMIN_URL` → `migrator` (migrations/seed).
- `DATABASE_URL` → `app_user` (the running app).

### 2.5 Apply schema + seed
From a host that can reach the cluster (a bastion, the app host, or via SSM port-forward —
**never** by making the DB public):

```bash
export DATABASE_URL="$DATABASE_ADMIN_URL"   # migrator role for DDL
./scripts/migrate.sh                          # db/migrations/0001..0008
./scripts/seed.sh                             # db/seed/seed.sql (49 packages + lookups)
```

`migrate.sh` and `seed.sh` are plain `psql` wrappers today (see `db/README.md`). Once the
schema is signed off, wire a real migration runner (Drizzle Kit or dbmate) so versioning is
tracked going forward — the existing SQL files become the baseline. **DECISION (§10).**

Sanity check after loading:
```sql
SELECT count(*) FROM package;          -- expect 49
SELECT count(*) FROM nickname_group;   -- expect 38
SELECT extname FROM pg_extension;      -- pgcrypto, pg_trgm, citext present
```

### 2.6 Backups
- Aurora automated backups: retention **≥ 7 days** (prod), PITR enabled.
- Take a **manual snapshot before every migration** in production.
- Periodically test a restore into a scratch cluster — an untested backup isn't a backup.

---

## 3. Object storage (photos, receipts, brochures)

- Create a **private** bucket (e.g. `talon-lodge-media`); **block all public access**.
- Access pattern: the backend issues **presigned URLs** for upload and download. Objects are
  never world-readable; the browser uploads/downloads directly via short-lived signed URLs.
- CORS: allow `PUT`/`GET` from `PUBLIC_BASE_URL` only.
- IAM: a dedicated user/role with `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` scoped to
  **that bucket ARN only**. Put its keys in Secrets Manager (`S3_ACCESS_KEY_ID` / `_SECRET`).
- Lifecycle: optional — expire orphaned temp-upload prefixes after N days.
- **Cloudflare R2 alternative:** same code path (S3-compatible); set `S3_ENDPOINT`. Cheaper
  egress if the media is heavily viewed.

> The real talonlodge.com photo URLs and Matterport links in the seed data are just external
> URLs and are fine as-is. Only *newly uploaded* files need this bucket.

---

## 4. Backend service (Node + TypeScript)

### 4.1 Host prep (Option A — EC2 + pm2)
- AMI: **Amazon Linux 2023**, in a **public subnet** (or private + ALB).
- Install Node 20 LTS (via `nvm` or `dnf`), `git`, and `pm2` (`npm i -g pm2`).
- Create a deploy user; app lives in e.g. `/opt/talon-lodge-platform`.

### 4.2 Configuration
- Copy [`.env.example`](../.env.example) → `.env`, populate from **Secrets Manager** at
  deploy time (do not hand-edit secrets onto the box). See the file for the full variable list.
- Key rule: **`ANTHROPIC_API_KEY` lives only here, server-side.** The AI-suggest endpoints
  call Anthropic from the backend; the browser calls *our* endpoint, never Anthropic directly
  (SPEC §5). Any design that puts the key in frontend code is wrong.

### 4.3 Run under pm2
```bash
cd /opt/talon-lodge-platform
npm ci --omit=dev
npm run build            # compiles TS
pm2 start dist/server.js --name lodge-api --time
pm2 save && pm2 startup  # survive reboots
```
- Expose the app on `PORT` (e.g. 8080) bound to `127.0.0.1`; only nginx talks to it.
- Health endpoint: implement `GET /healthz` (checks DB connectivity) for the proxy/ALB.

### 4.4 Option B notes (ECS Fargate)
- Containerize with a small multi-stage Dockerfile (build TS → run `node dist/server.js`).
- Inject env from Secrets Manager via the task definition.
- Put the service behind an ALB target group on `/healthz`.
- Run migrations as a **one-off task** (same image, command `./scripts/migrate.sh`) — not on
  container boot, to avoid races when multiple tasks start.

---

## 5. Reverse proxy & TLS

**Option A — nginx + certbot on the EC2 host:**
```nginx
server {
  listen 443 ssl;
  server_name platform.talonlodge.com;
  # ssl_certificate / ssl_certificate_key managed by certbot

  location /api/ {
    proxy_pass http://127.0.0.1:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
  location / {                      # static React build
    root /opt/talon-lodge-platform/web/dist;
    try_files $uri /index.html;
  }
}
# redirect :80 -> :443
```
- `certbot --nginx -d platform.talonlodge.com` for Let's Encrypt; auto-renew via timer.

**Option B — ALB + ACM:** terminate TLS at the ALB with an ACM cert; forward to the app
target group. Serve the React build from **CloudFront + S3** instead of nginx.

---

## 6. Networking & security groups

- **DB security group:** inbound `5432` **only** from the backend's security group. No `0.0.0.0/0`, ever.
- **Backend security group:** inbound `443` (or from the ALB SG); outbound to DB SG, S3
  (via gateway endpoint if possible), SES, and Anthropic (443).
- Aurora stays in **private subnets** with no public IP.
- Admin DB access: via a bastion or **SSM Session Manager port-forwarding**, not by opening
  the DB to the internet.
- Prefer an **S3 VPC gateway endpoint** so media traffic doesn't traverse the public internet.

---

## 7. Email (SES) — for guest magic-link auth

- Verify the **sending domain** (`talonlodge.com`) in SES; add DKIM + SPF DNS records.
- Move out of the SES sandbox (request production access) before real guests use it.
- `MAIL_FROM` (e.g. `no-reply@talonlodge.com`) and `AWS_SES_REGION` go in `.env`.
- Guest auth is **magic link** (matching the legacy pattern, SPEC §6); staff auth is separate
  (real per-user accounts + roles). The auth implementation itself is still to be built —
  this just readies the email path it will need.

---

## 8. Observability & operations

- **Logs:** ship pm2/app logs to CloudWatch (or the ALB/ECS log group). Structured JSON logs.
- **Alarms:** DB CPU / connections / free storage; app 5xx rate; host disk.
- **Metrics worth watching early:** DB connection count (size the pool below the instance's
  `max_connections`), and slow queries on the matching engine once it's live.
- **Runbook basics:** how to roll back a deploy (pm2 previous release / prior task def), how
  to restore a snapshot, who gets paged.

---

## 9. Environments & CI/CD

- Three tiers: **local** (docker-compose Postgres, see `db/README.md`), **staging**, **prod**.
- Never point staging at the prod DB or bucket. Separate cluster + bucket per tier.
- Suggested deploy flow:
  1. CI builds + runs tests (backend unit tests, matching-engine tests).
  2. Build artifact/image; push.
  3. Run DB migrations as a gated step (with a fresh snapshot taken first in prod).
  4. Deploy backend (pm2 reload / ECS new task); deploy static frontend (S3 sync + CloudFront invalidation).
  5. Smoke test `/healthz` and a couple of read endpoints.

---

## 10. Decisions to confirm before provisioning

These are deliberately **not** decided in code — get Phil's call (SPEC §6):

1. **Deploy shape:** EC2+pm2 (A) vs ECS Fargate (B). Reuse an existing Talon EC2/VPC, or a
   dedicated one for this platform?
2. **Region** (align with existing Talon AWS resources).
3. **Migration runner:** stay on plain psql, or adopt Drizzle Kit / dbmate now.
4. **Frontend serving:** nginx on the app host vs CloudFront+S3.
5. **Object storage:** S3 vs Cloudflare R2.
6. **Domain/subdomain** for the platform (`platform.talonlodge.com`?) and for the Guest Portal.
7. **Payments** (Stripe) and **real availability locking** — flagged unbuilt in SPEC §6;
   affect infra later (webhook endpoints, idempotency), not the initial stand-up.

---

## Appendix — non-negotiables carried from the prototype's failure modes
(These are hard requirements, not preferences — each is a failure already observed once.)
- No browser-storage-as-database — Aurora is the source of truth.
- No client-side AI calls — the Anthropic key is server-side only.
- No base64 "photo uploads" — real object storage from day one.
- No single-shared login — real per-user staff auth + separate guest auth.
