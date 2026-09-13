# PHASE 11-T — Customer runtimes: DispatchOS as a template instance

## STATUS: PENDING — NOT STARTED

**starts after: Phase 11 gate**

> **ORDERING (O1).** Each phase's own "Start after" line is authoritative. The
> QUEUED headers' serial chain was a paste convenience and is **WITHDRAWN**.
> Dependency graph:
>
> ```
> 10 → 11 → { 11-T, 18 }
> 11 → 12 → { 13, 14, 17 }
> 13 → 16          14 → 15          { 15, 16, 18 } → 19
> ```
>
> Builds run **concurrently in separate build dirs** when dependencies are met
> (R3', R6'). GPU PROOF steps (12f, 13e/13f, 14e, 16 runs, 17e) execute **one at a
> time through the governor** — train is never evicted, so a 13e run finishes
> before 14e's contention test starts.


Queued 2026-09-13 by Garrett with "QUEUED — do not start." Spec recorded verbatim
so the phase is self-contained when picked up. Nothing built, configured, started
or acquired. Per R14, `127.0.0.1:8800` remains untouched.


---

## SETTLED

- **S1** One template, many instances: `symoneural-dispatch@.service` reads
  `/etc/symoneural/tenants/%i/{tenant.json,units.json,api.env,accounts.env}`,
  binds `127.0.0.1:<port from tenant.json>`. Binaries shared; config differs.
- **S2** One card, one governor. Tenants never own a lock; all GPU units queue on
  the estate governor, tagged with the tenant name in the holder record.
- **S3** A tenant rack shows only its own units and receipts. Operator surfaces
  (Studio, Exp, Rack power, Miner, ASIC) never appear in a tenant's `units.json`.
- **S4** Tenant readiness is set by its units: CPU/NET units live now; Chat after
  Phase 12; Image/Sigils after Phase 14. Units not yet buildable are listed
  offline with reason "awaiting phase N", never hidden.
- **S5** First tenant name: `donnie`. Units `{ravencalc, project, coder, streamer}`
  unless Garrett supplies a list; chat and image offline "awaiting phase 12/14".

## ITEMS

- **11T-a** `Symoneural-API/app`: tenant-aware — config root from
  `SYMON_TENANT_DIR`, port from `tenant.json`, units from its `units.json`,
  tokens/accounts from its env files, receipts under `run/tenants/<name>/`. The
  estate's own instance is tenant `symoneural`.
- **11T-b** `meta-symoneural`: `symoneural-dispatch@.service` (template) replacing
  the single unit; hardening identical; `%i` wherever a path or port differs.
- **11T-c** `symoneural-secrets`: add `--tenant NAME` — writes
  `tenants/NAME/api.env` and `accounts.env` with fresh tokens, a `tenant.json`
  (name, port, display name, units), manifest rows namespaced `tenants/NAME/`.
  Adopt the tool's source into `meta-symoneural/tools/` with a recipe.
- **11T-d** Site: generators take a tenant and emit its rack page reading its own
  `/api/status`; branded with the tenant display name.
- **11T-e** Governor: holder record `"<tenant>/<surface> <pid>"`; two tenants
  requesting the same surface class queue in order; test with two RavenCalc
  requests on two instances and two mock GPU holds (governor only, no engine).
- **11T-f** Stand up donnie: `sudo symoneural-secrets setup --tenant donnie
  --non-interactive`; `systemctl start symoneural-dispatch@donnie`; its rack shows
  its units; a RavenCalc request answers.

## GATE

`@symoneural` (:8801) and `@donnie` run from the same binaries; donnie's
`/api/status` shows only donnie's units; operator surfaces absent; governor queue
test passes; **:8800 untouched**.

## COMMIT

`phase 11-T: DispatchOS as a systemd template; first tenant donnie`

## RETURN

- TEMPLATE instances (name:port); binaries shared YES/NO
- DONNIE units live / offline-awaiting; page rendered; RavenCalc answered
- GOVERNOR queue order preserved YES/NO
- SECRETS `tenants/donnie` manifest rows; no value in git: verified
- DECISIONS FOR GARRETT: none

---

# PHASE 11-T ADDENDUM — Accounts: request → verify → approve with level → auto-configured token

All CPU, no lock. Mail via `mail.env` (R13); SMTP is provisioned and tested.

**Readiness check against R13 (already verified in Phase 10):** all seven
`mail.env` keys are `status: set` — `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
`SMTP_PASS`, `MAIL_FROM`, `MAIL_ADMIN`, `ACCOUNTS_PUBLIC_URL`. `SYM_ACCOUNTS_SECRET`
and `SYM_ACCOUNTS_ENABLED` are set in `api.env`, as are `SYM_OWNER_EMAIL` and
`SYM_OWNER_TOKEN` (R15). **No human action is needed to start this phase.**

## SETTLED

- **S6** Entry point: `symoneural.com/demo/dispatchos.html` — the DispatchOS rack
  read-only for anyone, plus one email field: "Set up your account".
- **S7** Nothing reaches Garrett until the customer has proven the email is theirs.
- **S8** Garrett's approval is the ONLY manual step; everything after his click is
  automatic.
- **S9** Approve/deny links open a confirmation page; the decision is a POST from
  it. **A GET never changes state** — mail scanners prefetch links.
- **S10** Access levels, enforced server-side by scope, configurable per tenant:

  | level | scope |
  |---|---|
  | `viewer` | GET `/api/status`, receipts, rack page |
  | `user` | viewer + POST to the tenant's enabled units |
  | `operator` | user + tenant admin: units on/off, all receipts, issue/revoke keys |
  | `owner` | everything, every tenant (R15; bootstrapped from `SYM_OWNER_EMAIL`) |

- **S11** Tokens: per account, random 32 bytes, stored as SHA-256, shown to the
  customer exactly once by the page; revocable by owner/operator; rotatable by the
  customer. Human sign-in is a magic link; the token is for the page and native
  clients.

## ITEMS

- **T-1** `POST /api/accounts/request {email, tenant, note?}`: rate-limited per IP
  and email; store `{id, email, tenant, ip, ua, created, state=pending}`; send a
  verification link `ACCOUNTS_PUBLIC_URL/demo/dispatchos.html?verify=<code>`
  (random, hashed at rest, single use, 15 min). Page: "check your email".
- **T-2** `?verify=<code>` → `POST /api/accounts/verify` → `state=verified` → ONE
  email to `MAIL_ADMIN`: email, tenant, note, ip/ua, time, and four links —
  *Approve as viewer · Approve as user · Approve as operator · Deny* — each a
  signed token `HMAC(SYM_ACCOUNTS_SECRET, id|level|exp)`, exp 7 days, single use
  enforced by the store's state machine.
- **T-3** `GET /api/accounts/decide?t=` renders a confirmation page (request,
  level, optional "dedicated runtime: slug" using 11-T provisioning) with ONE
  button; POST performs it. CLI equivalent: `symoneural-cli accounts list |
  approve <id> --level user [--tenant slug] | deny <id>` (authenticated by
  `SYM_OWNER_TOKEN`).
- **T-4** On approve: create account `{email, tenant, level}`; generate the token
  (S11); store the hash; create a one-time ACTIVATION code (24 h); email the
  customer `ACCOUNTS_PUBLIC_URL/demo/dispatchos.html?activate=<code>`.
  **On deny: `state=denied`; email only if `tenant.json notify_denied`.**
- **T-5** `?activate=<code>` → `POST /api/accounts/activate` →
  `{token, level, tenant, email}` **ONCE** → page stores the token in
  localStorage, shows it once with a copy button and "this is shown once",
  switches the header to "signed in as `<email>` · `<level>`", and sends
  `Authorization: Bearer <token>` on every call. Permitted units become
  interactive; others stay visible, read-only. Cleared site data →
  `POST /api/accounts/signin {email}` → magic link → new token.
- **T-6** Scopes enforced in **one** dependency on every tenant route; a tenant-A
  token is rejected by tenant B.
- **T-7** Owner (R15) bootstrapped at first start; owner and operators: list,
  revoke, rotate, change level. **Every state change is a receipt.**
- **T-8** Mail: one sender over `smtplib` — STARTTLS on 587 or implicit TLS on 465
  — **plain text, no customer-controlled HTML**, From `MAIL_FROM` (must be
  `SMTP_USER` or one of its Zoho aliases).
- **T-9** Tests with a **fake SMTP sink**: full path; prefetch-safety; expiry;
  single-use; cross-tenant rejection; **token never appears in any log or receipt**.

## GATE (addendum)

Clean browser: request → verification → admin email with four links → approve as
user via the confirmation page → activation → token shown once, header changes → a
RavenCalc request succeeds with the bearer token and fails without; **a GET on the
approve link changed nothing**; owner account exists; **:8800 untouched**.

## COMMIT (addendum)

`phase 11-T: accounts request/verify/approve with levels; owner bootstrap; auto-configured tokens; demo/dispatchos.html`

## RETURN (addendum)

- FLOW each step timestamped from one real run; prefetch test passed
- LEVELS scopes enforced; cross-tenant rejection passed; owner bootstrapped
- MAIL Zoho host used; approval email received at `MAIL_ADMIN`
- TOKENS never in logs: grep evidence
- DECISIONS FOR GARRETT: none

## READINESS

Spec is **complete** — T-1 through T-9 all supplied. Secrets verified present in
Phase 10: all seven `mail.env` keys `set`, plus `SYM_ACCOUNTS_SECRET`,
`SYM_ACCOUNTS_ENABLED`, `SYM_OWNER_EMAIL`, `SYM_OWNER_TOKEN`. **No human action is
required to begin.** Blocked only on the Phase 11 gate.
