# SyMoNeuRaL — Garrett's Operator Checklist

**Revision 1 · 13 September 2026.** One file. Everything that is yours to do, in the order it has to happen, with the exact commands, plus every prompt you still owe the coder as an appendix. If it is not in this file, it is not on your plate — the coder or the advisor has it.

You are not behind. The coder is on Phase 10 and it has work for about two days before it needs anything from you beyond pasting the next phase. Your part is about 40 minutes today, then one small task per phase.

---

## The one rule

**The coder works; you do five kinds of things:** run the secrets tool, click in two dashboards (Cloudflare, Zoho), paste the next phase when a gate passes, decide what a customer gets, and read the morning report. Nothing you do needs a password from anyone, and you never send a password to the advisor.

---

## 0. Where things stand

| Thing | State |
|---|---|
| Estate | 41 sources at pinned revisions · acquisition CLOSED · HEAD past `3e36972` with Phase 10 in progress |
| Built | Ravencalc 4/6 · Fortran toolchain · Rust offline compile PROVEN (stratum) · pristine class live · 38 recipes in `meta-symoneural` |
| Coder | Phase 10 (curation + pristine). Phases 11, 12, 13 already pasted and queued |
| Host | 94 GB RAM · **32 GB swap done** · RTX 5070 Ti · CUDA 13.3 |
| Mail | Zoho: MX, SPF and two DKIM selectors already live in Cloudflare DNS — only an app password missing |
| Domain | `symoneural.com` A → `96.37.45.61`, Cloudflare-proxied; nothing answering → the 522 |
| Secrets | `/etc/symoneural/` exists with placeholder text — the tool replaces it |
| Demo | `127.0.0.1:8800/livestack` is the current site and is **read-only for the coder** (rule R14) |

---

## 1. Today — about 40 minutes

### 1.1 Zoho app password (5 min)
1. Sign in at **accounts.zoho.com** as `symonsayadmin@symoneural.com`.
2. **Security → App Passwords → Generate New Password.** Name it `symoneural-dispatch`. Copy it once; you will paste it in 1.2.
3. Check your plan: **Zoho Mail Admin Console → Subscription.** SMTP needs *Mail Lite* or above. The free plan will fail authentication no matter what.

### 1.2 Run the secrets tool (10 min)
Save `symoneural-secrets.py` (attached in chat) somewhere, then:

```bash
sudo install -m 0755 symoneural-secrets.py /usr/local/sbin/symoneural-secrets
sudo symoneural-secrets setup
```

Answer only what it asks. **Blank = leave unset; the dependent unit simply stays off. Nothing blocks.**

| Prompt | What to enter now |
|---|---|
| `TUNNEL_TOKEN` | blank (comes in §2.1) |
| `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` | blank (comes in §2.2) |
| `SMTP_USER` | `symonsayadmin@symoneural.com` |
| `SMTP_PASS` | the Zoho app password from 1.1 |
| `SYM_GATEWAY_CONTRACT` / `_BENEFICIARY` | blank |
| `SYM_MINER_POOL` / `_WALLET` | blank |

Everything else is generated for you: nine surface tokens, the accounts secret, **your owner token**, two ed25519 signing keypairs (replacing the one lost in `/tmp`), the models directory, and `manifest.json` which the coder reads. Then:

```bash
symoneural-secrets status          # names and fingerprints only — this is what the coder sees
sudo symoneural-secrets verify     # must print VERIFY: PASS
```

### 1.3 Prove mail works (2 min)
```bash
sudo python3 - <<'EOF'
import smtplib, ssl
from email.message import EmailMessage
env = dict(l.strip().split("=",1) for l in open("/etc/symoneural/mail.env") if "=" in l and not l.startswith("#"))
m = EmailMessage(); m["From"]=env["MAIL_FROM"]; m["To"]=env["MAIL_ADMIN"]; m["Subject"]="SyMoNeuRaL mail test"
m.set_content("If you can read this, Zoho SMTP, the app password and DKIM are working.")
with smtplib.SMTP(env["SMTP_HOST"], int(env["SMTP_PORT"])) as s:
    s.starttls(context=ssl.create_default_context()); s.login(env["SMTP_USER"], env["SMTP_PASS"]); s.send_message(m)
print("sent")
EOF
```
`sent` + the message in your inbox = done. A `535` error with a correct app password = the free plan (see 1.1 step 3).

### 1.4 One DNS record (3 min)
Cloudflare → symoneural.com → DNS → **Add record**: Type `TXT`, Name `_dmarc`, Content:
```
v=DMARC1; p=quarantine; rua=mailto:symonsayadmin@symoneural.com
```
This completes SPF + DKIM + DMARC so approval emails to customers land in inboxes.

### 1.5 Your owner access — nothing to do
`SYM_OWNER_EMAIL=symonsayadmin@symoneural.com` is now in `api.env`. When the accounts service first starts (Phase 11-T) it creates your **owner** account: every tenant, every approval, every revocation, the CLI. You sign in by a magic link to that mailbox. `SYM_OWNER_TOKEN` authenticates `symoneural-cli`. There is no password, so there is nothing to hash and nothing to send anyone.

### 1.6 Send the coder one block now (2 min)
Paste **Appendix A1 (ADVISOR ANSWERS)** into the coder session now — it corrects the swap premise it is still working under, settles the Rust install rule, and makes the :8800 site read-only. It is safe to paste mid-phase.

### 1.7 Decide Donnie's units (whenever you can — 1 line)
Phase 11-T stands up his runtime with `{ravencalc, project, coder, streamer}` unless you say otherwise. Chat needs Phase 12; Image needs Phase 14. Tell the coder (or the advisor) the list and it replaces S5.

---

## 2. This week — one task per phase, when its gate approaches

### 2.1 Cloudflare tunnel — do before Phase 15 (10 min)
1. Cloudflare → **Zero Trust → Networks → Tunnels → Create a tunnel → Cloudflared**. Name: `symoneural`. Copy the token.
2. **Public Hostname** tab: `symoneural.com` → `HTTP` → `localhost:80`. Add `www.symoneural.com` the same way. Cloudflare will offer to replace the existing A record with the tunnel CNAME — **say yes**.
3. On the box:
```bash
sudo symoneural-secrets setup --only TUNNEL_TOKEN
```
The coder builds and runs `cloudflared` in Phase 15 and reads the token from the manifest. Until then the quick tunnel (`trycloudflare`) proves the path without an account.

### 2.2 Spotify — do before Phase 19 (10 min)
1. **developer.spotify.com → Dashboard** → your existing app → **Settings → rotate/reset the client secret.** The old one is in a tarball that has travelled.
2. Same app (or a new one, `SyMoNeuRaL Remix`): tick **Web API**; Redirect URI exactly `https://symoneural.com/api/remix/callback`; save.
3. On the box:
```bash
sudo symoneural-secrets setup --only SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET
```
Know two Spotify facts: a new app is in development mode (25 allow-listed users) until you request extended quota, and audio-features / analysis / recommendations are not available to new apps — Remix's intelligence comes from Chat.

### 2.3 Read two sections of the handbook (20 min)
`SyMoNeuRaL-Build-Manuals-v3.html` → **How the stack works** and **The plan, phases 10–19**. Everything the coder prints will then have a place to land.

---

## 3. The prompt schedule — when the coder says X, you paste Y

The coder reports `GATE PASSED` at the end of each phase and writes `generated/phase-NN-report.md`. That report line is your cue.

| When the coder reports… | You paste (from Appendix) |
|---|---|
| anything, right now | **A1** ADVISOR ANSWERS |
| `phase 10 GATE PASSED` | nothing — Phase 11 is already queued |
| `phase 11 GATE PASSED` | **A2** Phase 11-T, then **A3** the Accounts addendum |
| `phase 11-T GATE PASSED` | nothing — Phase 12 is already queued |
| `phase 12 GATE PASSED` | nothing — Phase 13 is already queued (its own night) |
| `phase 13 GATE PASSED` | **A4** Phase 14 |
| `phase 14 GATE PASSED` | **A5** Phase 15 *(do §2.1 first)* |
| `phase 15 GATE PASSED` | **A6** Phase 16 |
| `phase 16 GATE PASSED` | **A7** Phase 17 |
| `phase 17 GATE PASSED` | **A8** Phase 18 |
| `phase 18 GATE PASSED` | **A9** Phase 19 *(do §2.2 first)* |

Always paste **A0 (COMMON)** above a phase if the coder session has been compacted or restarted since the last phase — it costs nothing and re-arms the rules.

**Remaining pastes: 9** (A1, A2, A3, A4–A9). There is no Phase 20.

---

## 4. What you never do — and the coder never does

- Never send the advisor a password, token, or secret. Fingerprints only (`symoneural-secrets status`).
- Never `git add .` or `git add -A` in the estate. Explicit paths, always.
- Never stop, restart or edit the `:8800` deployment while it is your demo (R14).
- Never run two `bitbake` commands in one build directory. Different directories are fine — you have 32 GB of swap.
- Never delete `sstate-cache`. It holds the LLVM and gcc builds that took hours; it is rsync'd to `/home/google/sstate-backup`.
- Never put weights, `.env` files or keys in git. Weights live in `/home/google/symoneural-models`; secrets in `/etc/symoneural`.

---

## 5. When the coder asks you something

Every phase is written so its report ends **`DECISIONS FOR GARRETT: none`**. If a report says anything else:

1. **`GARRETT ACTION: …`** → it is in this checklist (§1 or §2). Do it, then tell the coder "done".
2. **A question about *what a customer gets or pays*** → yours alone; the rule "never invent pricing" keeps it out of the coder's hands. Answer when ready; nothing blocks on it.
3. **Anything else** → paste the report to the advisor. That is a spec gap, not your problem.

---

## 6. Files and where they live

| File | What it is |
|---|---|
| `SyMoNeuRaL-Build-Manuals-v1.html` | the Yocto reading list |
| `SyMoNeuRaL-Build-Manuals-v2.html` | the estate handbook: stack, register, rack, models, procedures |
| `SyMoNeuRaL-Build-Manuals-v3.html` | v2 + plan 10–19, customer runtimes and onboarding, secrets and configuration (also the live page) |
| `symoneural-secrets.py` | the secrets tool — install to `/usr/local/sbin/symoneural-secrets` |
| `SyMoNeuRaL-Operator-Checklist.md` | this file |
| `/etc/symoneural/manifest.json` | what is set, fingerprints only — the coder reads it |
| `generated/phase-NN-report.md` | the coder's report per phase — your morning read |

---

## Appendix A — everything left to paste, in order

### A0 — COMMON (paste above any phase after a compact or restart)

```
COMMON — paste above every phase from 10 onward

MODE: autonomous. Nothing blocks on a human. A phase that needs a human ACTION
(account access, a secret, money) stops at its gate with the action written
in the report. A genuinely open decision is recorded under DECISIONS FOR
GARRETT and work continues on the next independent item.

STATE: read generated/phase-NN-report.md; resume from the first item not
marked DONE; append after every item. The file is the report.

RULES IN FORCE: R1–R9 and A1–A6, amended:
  A1'  Identity is the SHA. Prefer the latest stable release tag; where an
       upstream has no release line (stable-diffusion.cpp: master-N-sha),
       pin the commit and record tag_kind SNAPSHOT with the tag as context.
  A7   Acquisition happens only inside the phase that builds the component,
       from acquisition/pending-acquisitions.json. Nothing is cloned ahead of
       its build.
  R3'  One bitbake per build directory. Long compiles run in the background
       and other build directories may proceed. Git commits only at gates.
  R6'  Swap is 31 GiB. Concurrent builds in SEPARATE build directories are
       allowed; keep BB_NUMBER_THREADS "10" / PARALLEL_MAKE "-j 12" per dir.
  R10  sstate-cache is a protected asset: never deleted; rsync'd after every
       phase that built a toolchain component.
  R11  No recipe uses externalsrc. Every recipe inherits symoneural-pristine:
       ${S} is a disposable export of the acquired tree, asserted == SRCREV;
       B is always out of tree.
  R12  An empty ${D} after do_install is a FAILURE. Rust LIBRARY workspaces
       install their rlibs into ${PN}-staticdev.
  R13  SECRETS: /etc/symoneural/*.env is provisioned by symoneural-secrets
       (/usr/local/sbin). Read /etc/symoneural/manifest.json (no values). A
       unit whose secret is unset is configured OFF and named in the report.
       Never prompt, never generate, never commit a secret. EnvironmentFile=.
  R14  DEMO-CRITICAL: 127.0.0.1:8800 is read-only. Never stop, restart, edit
       or redeploy it. Capture from it by reading.
  R15  OWNER: SYM_OWNER_EMAIL / SYM_OWNER_TOKEN from api.env. First start of
       the accounts service creates the owner account at level `owner` (all
       tenants, approvals, revocations, CLI). Owner signs in by magic link.
       No password exists anywhere in the product.

PRODUCT LAYER: meta-symoneural/ and Symoneural-<Runtime>/app/ are tracked;
nothing of ours lives under src/*/source/. Weights live at
/home/google/symoneural-models (SYMON_MODELS_DIR); never in git.

PRECEDENCE: the estate being correct beats category purity. One GPU tenant per
job. train is never evicted. miner yields to everything. CPU and NET units
never take the lock. Gates are builds or live units. Never invent pricing.
```

### A1 — ADVISOR ANSWERS (paste now, mid-phase is fine)

```
ADVISOR ANSWERS — apply immediately; these amend COMMON (R6', R12', R13, R14, R15
as written in COMMON above).

Item 1  Agreed: 10f parity is re-verification, not a formality. Expect breakage;
        each difference is a finding with its log, not a rollback.
Item 2  Rust LIBRARY workspaces (stratum): do_install installs the rlibs into
        ${PN}-staticdev — a real artifact, non-empty ${D}, R12 stands. Binaries
        (sv2-apps pool/translator/jd, librespot) use cargo's install; sv2-apps is
        one recipe per workspace, four recipes.
Item 3  Phase 11a is non-blocking per R14: capture from :8800 by reading; if it is
        not serving, locate via `systemctl cat symoneural-api` → WorkingDirectory
        and capture from disk. Never start or stop it.
R6'     Swap is 31 GiB, not 0. Stop serialising builds for a false premise;
        separate build directories may run concurrently.
R13/R15 Secrets and the owner account come from /etc/symoneural via
        symoneural-secrets. Phase 11 adopts the tool's source into
        meta-symoneural/tools/ with a recipe and adds --tenant NAME.
```

### A2 — Phase 11-T (paste when `phase 11 GATE PASSED`)

```
PHASE 11-T — Customer runtimes: DispatchOS as a template instance
Start after: Phase 11 gate. Milestone: a second DispatchOS instance runs beside
the estate's own, from the same binaries, with its own units, tokens, accounts,
receipts and page — the shape every "Have one built" customer receives.

SETTLED
  S1  One template, many instances: symoneural-dispatch@.service reads
      /etc/symoneural/tenants/%i/{tenant.json,units.json,api.env,accounts.env},
      binds 127.0.0.1:<port from tenant.json>. Binaries shared; config differs.
  S2  One card, one governor. Tenants never own a lock; all GPU units queue on the
      estate governor, tagged with the tenant name in the holder record.
  S3  A tenant rack shows only its own units and receipts. Operator surfaces
      (Studio, Exp, Rack power, Miner, ASIC) never appear in a tenant's units.json.
  S4  Tenant readiness is set by its units: CPU/NET units are live now; Chat after
      Phase 12; Image/Sigils after Phase 14. Units not yet buildable are listed
      offline with reason "awaiting phase N", never hidden.
  S5  First tenant name: donnie. Units {ravencalc, project, coder, streamer}
      unless Garrett supplies a list; chat and image offline "awaiting phase 12/14".

ITEMS
  11T-a  Symoneural-API/app: tenant-aware — config root from SYMON_TENANT_DIR,
         port from tenant.json, units from its units.json, tokens/accounts from
         its env files, receipts under run/tenants/<name>/. The estate's own
         instance is tenant "symoneural".
  11T-b  meta-symoneural: symoneural-dispatch@.service (template) replacing the
         single unit; hardening identical; %i wherever a path or port differs.
  11T-c  symoneural-secrets: add --tenant NAME — writes tenants/NAME/api.env and
         accounts.env with fresh tokens, a tenant.json (name, port, display name,
         units), manifest rows namespaced tenants/NAME/. Adopt the tool's source
         into meta-symoneural/tools/ with a recipe.
  11T-d  Site: generators take a tenant and emit its rack page reading its own
         /api/status; branded with the tenant display name.
  11T-e  Governor: holder record "<tenant>/<surface> <pid>"; two tenants requesting
         the same surface class queue in order; test with two RavenCalc requests
         on two instances and two mock GPU holds (governor only, no engine).
  11T-f  Stand up donnie: sudo symoneural-secrets setup --tenant donnie
         --non-interactive; systemctl start symoneural-dispatch@donnie; its rack
         shows its units; a RavenCalc request answers.

GATE: @symoneural (:8801) and @donnie run from the same binaries; donnie's
      /api/status shows only donnie's units; operator surfaces absent; governor
      queue test passes; :8800 untouched.
COMMIT: "phase 11-T: DispatchOS as a systemd template; first tenant donnie"
RETURN
  TEMPLATE instances (name:port); binaries shared YES/NO
  DONNIE units live / offline-awaiting; page rendered; RavenCalc answered
  GOVERNOR queue order preserved YES/NO
  SECRETS tenants/donnie manifest rows; no value in git: verified
  DECISIONS FOR GARRETT: none
```

### A3 — Phase 11-T Accounts addendum (paste right after A2)

```
PHASE 11-T ADDENDUM — Accounts: request → verify → approve with level → auto-configured token
All CPU, no lock. Mail via mail.env (R13); if SMTP_* is unset the flow runs to the
point of sending and the report says so.

SETTLED
  S6  Entry point: symoneural.com/demo/dispatchos.html — the DispatchOS rack
      read-only for anyone, plus one email field: "Set up your account".
  S7  Nothing reaches Garrett until the customer has proven the email is theirs.
  S8  Garrett's approval is the ONLY manual step; everything after his click is automatic.
  S9  Approve/deny links open a confirmation page; the decision is a POST from it.
      A GET never changes state — mail scanners prefetch links.
  S10 Access levels, enforced server-side by scope, configurable per tenant:
        viewer    GET /api/status, receipts, rack page
        user      viewer + POST to the tenant's enabled units
        operator  user + tenant admin: units on/off, all receipts, issue/revoke keys
        owner     everything, every tenant (R15; bootstrapped from SYM_OWNER_EMAIL)
  S11 Tokens: per account, random 32 bytes, stored as SHA-256, shown to the
      customer exactly once by the page; revocable by owner/operator; rotatable by
      the customer. Human sign-in is a magic link; the token is for the page and
      native clients.

ITEMS
  T-1  POST /api/accounts/request {email, tenant, note?}: rate-limited per IP and
       email; store {id, email, tenant, ip, ua, created, state=pending}; send a
       verification link ACCOUNTS_PUBLIC_URL/demo/dispatchos.html?verify=<code>
       (random, hashed at rest, single use, 15 min). Page: "check your email".
  T-2  ?verify=<code> → POST /api/accounts/verify → state=verified → ONE email to
       MAIL_ADMIN: email, tenant, note, ip/ua, time, and four links —
         Approve as viewer · Approve as user · Approve as operator · Deny
       each a signed token HMAC(SYM_ACCOUNTS_SECRET, id|level|exp), exp 7 days,
       single use enforced by the store's state machine.
  T-3  GET /api/accounts/decide?t= renders a confirmation page (request, level,
       optional "dedicated runtime: slug" using 11-T provisioning) with ONE button;
       POST performs it. CLI equivalent: symoneural-cli accounts list | approve <id>
       --level user [--tenant slug] | deny <id>  (authenticated by SYM_OWNER_TOKEN).
  T-4  On approve: create account {email, tenant, level}; generate the token (S11);
       store the hash; create a one-time ACTIVATION code (24 h); email the customer
       ACCOUNTS_PUBLIC_URL/demo/dispatchos.html?activate=<code>. On deny:
       state=denied; email only if tenant.json notify_denied.
  T-5  ?activate=<code> → POST /api/accounts/activate → {token, level, tenant,
       email} ONCE → page stores the token in localStorage, shows it once with a
       copy button and "this is shown once", switches the header to "signed in as
       <email> · <level>", and sends Authorization: Bearer <token> on every call.
       Permitted units become interactive; others stay visible, read-only.
       Cleared site data → POST /api/accounts/signin {email} → magic link → new token.
  T-6  Scopes enforced in one dependency on every tenant route; a tenant-A token is
       rejected by tenant B.
  T-7  Owner (R15) bootstrapped at first start; owner and operators: list, revoke,
       rotate, change level. Every state change is a receipt.
  T-8  Mail: one sender over smtplib — STARTTLS on 587 or implicit TLS on 465 —
       plain text, no customer-controlled HTML, From MAIL_FROM (must be SMTP_USER
       or one of its Zoho aliases). SMTP_HOST unset → log the message, report
       "mail.env unset — flow complete up to send".
  T-9  Tests with a fake SMTP sink: full path; prefetch-safety; expiry; single-use;
       cross-tenant rejection; token never appears in any log or receipt.

GATE: clean browser: request → verification → admin email with four links →
      approve as user via the confirmation page → activation → token shown once,
      header changes → a RavenCalc request succeeds with the bearer token and fails
      without; a GET on the approve link changed nothing; owner account exists;
      :8800 untouched.
COMMIT: "phase 11-T: accounts request/verify/approve with levels; owner bootstrap; auto-configured tokens; demo/dispatchos.html"
RETURN
  FLOW each step timestamped from one real run; prefetch test passed
  LEVELS scopes enforced; cross-tenant rejection passed; owner bootstrapped
  MAIL provider host used, or "unset — completed up to send"
  TOKENS never in logs: grep evidence
  DECISIONS FOR GARRETT: none
```

### A4 — Phase 14 (paste when `phase 13 GATE PASSED`)

```
PHASE 14 — Diffuse: Image and Sigils live, the lock under contention
Start after: Phase 12 gate (independent of 13). Milestone: sd-cli built with
CUDA renders SymonImage F1 at 768² and trades the card with Chat.

SETTLED
  S1  Each ggml carrier builds its own vendored ggml as upstream ships it; the
      three-ggml collision stays recorded UNRESOLVED.
  S2  whisper.cpp is CPU, GGML_CUDA=OFF.
  S3  Acquire here (A7): stable-diffusion.cpp pinned SNAPSHOT 7f410a37
      (master-859-7f410a3), diffusers, rembg, whisper.cpp, and onnxruntime
      (microsoft/onnxruntime, MIT — rembg requires it; CPU-only build).

ITEMS
  14a symoneural-stable-diffusion-cpp: cmake, SD_CUDA, CMAKE_CUDA_ARCHITECTURES=120;
      package sd-cli. Provenance row: ggml submodule = leejet/ggml fork.
  14b onnxruntime CPU; then rembg. whisper.cpp CPU; package whisper-cli.
  14c Register rows image, image-aux, asr, cutout: FOUND/FETCHED/ABSENT by sha256
      per Phase 12 S3.
  14d Register image and sigils units with launch lines (sd-cli --backend te=cpu
      --vae-tiling --diffusion-fa, 4 steps, cfg 1.0, euler); matte and PNG encoder
      in Symoneural-Diffuse/app/.
  14e Contention: alternate POST /api/chat and POST /api/image ten times; log each
      eviction with drain time and VRAM before/after.

GATE: 768² render measured within 20% of 11.2 s; ten alternations, zero stale
      holders, every drain under 60 s; a cutout and a transcription complete on
      CPU during a render; clean.
COMMIT: "phase 14: Diffuse acquired and built; onnxruntime; lock proven under contention"
RETURN
  ACQUIRED five: tag/SNAPSHOT → SHA, licence files, collisions
  RENDER seconds measured, VRAM peak;  CONTENTION evictions, max drain, stale holders
  CPU-BESIDE-GPU cutout ms, transcription ms
  DECISIONS FOR GARRETT: none
```

### A5 — Phase 15 (paste when `phase 14 GATE PASSED`; do §2.1 first)

```
PHASE 15 — Gateway and cutover: symoneural.com served entirely from the estate
Start after: Phase 14 gate. Milestone: the 522 goes away through a tunnel;
every process behind it traces to a pin.

SETTLED
  S1  Tunnel posture, outbound only.  S2  Caddy for static and compression;
  FastAPI does all routing.  S3  Authentication before public (the accounts
  service from 11-T).  S4  Acquire here (A7): caddy, cloudflared, tronpy,
  coincurve. Web's workerd/workers-sdk fold into Gateway's runtime folder.
  OUT OF SCOPE BY RULE: account tiers and pricing (never invent pricing).

ITEMS
  15a caddy and cloudflared via the go classes with tracked module closures;
      symon-gateway via cargo; limiter.go → wasm with GOOS=wasip1 so the gateway
      leaves native-fallback.
  15b Caddyfile in meta-symoneural: August's routing intent; servers block with
      trusted_proxies for the tunnel's local peer and client_ip_headers
      CF-Connecting-IP; spoofed X-Forwarded-For test proves the limiter keys on
      the real client.
  15c Accounts required on /api/chat, /api/image, /api/remix per 11-T scopes;
      /api/status and /demo/dispatchos.html public.
  15d Site generators in Symoneural-UI/app/ emit pages reading the bus;
      manifest.json, brand icons, service worker caching the shell and never
      /api; deploy to /var/www/symoneural.
  15e SBOM for every recipe in packagegroup-symoneural-rack; cve-check; both on
      /receipts.
  15f Quick tunnel (cloudflared tunnel --url http://127.0.0.1:80) reached from a
      second network. Named tunnel: TUNNEL_TOKEN from the manifest; if unset,
      report "TUNNEL_TOKEN unset" and stop at the quick-tunnel proof.

GATE: quick tunnel live with chat streaming; 15b spoof test passes; SBOM and
      cve-check on /receipts; named tunnel LIVE or "TUNNEL_TOKEN unset" reported.
COMMIT: "phase 15: gateway stack from the estate; tunnel; auth on public surfaces; SBOM on receipts"
RETURN
  ACQUIRED four: tag → SHA, licence files, collisions
  BUILT caddy / cloudflared / symon-gateway / limiter.wasm
  EDGE quick tunnel reached YES/NO; named tunnel LIVE / TUNNEL_TOKEN unset
  AUTH endpoints gated;  SBOM recipes covered, CVEs by severity
  DECISIONS FOR GARRETT: none
```

### A6 — Phase 16 (paste when `phase 15 GATE PASSED`)

```
PHASE 16 — Studio and Reinforce as a live unit
Start after: Phase 13 gate. Milestone: a full sft preset runs from the rack,
passes evaluation, and is promoted to serving by configuration.

SETTLED
  S1  train is never evicted.  S2  Promotion by units.json, never by copying into
  a source tree.  S3  MCP server is python-sdk; fastmcp not acquired.  S4  Corpus:
  path and sha256 only.  S5  The 27B adapter IS evaluated on the Q2_K_XL base; an
  unevaluated adapter is never served (label measured, never projected).

ITEMS
  16a Symoneural-Studio/app/: registry (HF cache + GGUF dir), presets (smoke,
      voice, recall, longform, prefer=DPO, reward=GRPO, probe), VRAM planner
      validated against measured 7B ~12 GB and 27B 14.26 GiB, job runner under
      `with train`, outputs run/reinforce/adapters/<job>.
  16b Evaluation harness: held-out prompts by corpus path, perplexity and
      behaviour probes, thresholds as measured baselines.
  16c Export to GGUF; promote via units.json; Chat reloads.
  16d Agent loop on python-sdk; run_command and write_file confined to
      Symoneural-Studio/work/; token-gated (user level or above).
  16e Exp plugin runtime packaged; hot-reload double-run fixed with a test.
  16f studio unit with reinforce (gpu) and exp (cpu) sub-units; page.
  16g Evaluate the 27B adapter with 16b; serve only if it passes; record either way.

GATE: one sft run from the UI produces an adapter that passes 16b and is served;
      a chat request during training reports queued, never evicts; 16g recorded.
COMMIT: "phase 16: Studio live — training bay, eval harness, promotion by config, MCP on python-sdk"
RETURN
  RUN preset, steps, wall time, peak VRAM;  EVAL metrics vs baseline
  PROMOTE adapter sha256 served YES/NO;  AGENT tools, confinement test
  27B evaluated: PASS / FAIL with numbers
  DECISIONS FOR GARRETT: none
```

### A7 — Phase 17 (paste when `phase 16 GATE PASSED`)

```
PHASE 17 — Crypto and Miner: Stratum V2 on the LAN, a GPU miner that yields
Start after: Phase 12 gate. Milestone: pool and translator run from estate
binaries, an SV1 miner connects through the translator, and the GPU miner yields
the card to Chat within seconds.

SETTLED
  S1  GPL-3 miners are separate processes, never linked.
  S2  Pool and wallet come from miner.env (SYM_MINER_POOL / SYM_MINER_WALLET).
      Unset → benchmark only; mining stays off; no question returns.
  S3  The governor becomes a daemon: UNIX socket API, holder registry, eviction
      hooks, drain, the yield protocol from docs/specs/miner-preemption.md.
  S4  Acquire here (A7): kawpowminer (GPL-3, own src/gpu), pyasic (licence
      characterised from the tree).

ITEMS
  17a sv2-apps pool, translator, JD as LAN-bound services from templates.
  17b kawpowminer against the estate CUDA for sm_120; process boundary recorded.
  17c pyasic control service; scan opt-in, private ranges only.
  17d symoneural-governor daemon per S3; dispatch and launch paths switch to the
      socket; the mkdir mutex stays as crash-safe fallback.
  17e Yield test: kawpowminer in benchmark under `with miner`; request /api/chat;
      measure request-to-chat-holds-the-card.

GATE: SV1 test miner (or the QEMU Antminer board) authenticates through the
      translator; kawpowminer hashes and yields in under 15 s measured; no wallet
      string in the tree.
COMMIT: "phase 17: Stratum V2 services; governor daemon with yield; GPU miner as separate process"
RETURN
  ACQUIRED two: tag → SHA, licences as read
  SV2 up / SV1 accepted;  MINER MH/s and yield time measured
  GOVERNOR socket calls served, fallback exercised
  DECISIONS FOR GARRETT: none
```

### A8 — Phase 18 (paste when `phase 17 GATE PASSED`)

```
PHASE 18 — Live, Streamer, Voice: the NET and CPU units
Start after: Phase 11 gate. Milestone: a live source streams to the page over HLS
from estate gstreamer; speech transcribes on CPU during a render.

SETTLED
  S1  gstreamer is SyMoNeuRaL-owned (D2); build only needed plugin sets; accept no
      LICENSE_FLAGS commercial; record what each exclusion cost.
  S2  Segmenter is gstreamer, not ffmpeg; hls.js stays in the browser.
  S3  Voice is CPU-only.  S4  Acquire here (A7): piper (MIT) with its voice
  model's licence in the register.

ITEMS
  18a symoneural-gstreamer: core, base, good, HLS sink (hlssink3 from
      gst-plugins-rs via cargo, else hlssink2 only if S1 permits); plugin list recorded.
  18b Live: pipeline units — videotestsrc, then v4l2, screen, RTMP/SRT ingest —
      segments to tmpfs served by Caddy; live unit registered.
  18c Streamer: August's IPTV contract (SSRF guard, Xtream/M3U, EPG, two slots)
      rebuilt in Symoneural-Streamer/app/ on the gstreamer segmenter; hls.js from
      Phase 10's recipe.
  18d Voice: whisper-cli unit at /api/voice with row and page; piper TTS.

GATE: test pattern over HLS with measured latency under 10 s; an M3U channel
      plays; a 3 s clip transcribes on CPU during a render; clean.
COMMIT: "phase 18: gstreamer HLS live, Streamer rebuilt, Voice unit with TTS"
RETURN
  GST plugins built, exclusions and cost;  LIVE latency, sources
  STREAMER channels, guard tests;  VOICE ASR ms during render, TTS voice + licence
  DECISIONS FOR GARRETT: none
```

### A9 — Phase 19 (paste when `phase 18 GATE PASSED`; do §2.2 first)

```
PHASE 19 — Tune, Remix, Adaptive-Fabric, contract freeze, estate closure
Start after: Phases 15 and 16 gates. Milestone: the card is a managed device on
the bus, every shipped recipe compiles with the network off, the API is frozen at
v1 for the native clients, and the estate is tagged.

SETTLED
  S1  Tune: telemetry and power limits via NVML now; fan and clock deferred.
  S2  Remix: official Spotify Web API over OAuth PKCE (httpx) for library, search,
      playlists, playback control; librespot an optional personal-device Connect
      daemon with its terms caveat on the page; audio-features, analysis and
      recommendations not used. Credentials from spotify.env; if unset the Remix
      unit is configured OFF and reported. No question returns.
  S3  FreeToken tested unmodified on Common's torch 2.14; if it does not run,
      Adaptive-Fabric is DEFERRED with evidence.
  S4  Offline proven by BB_NO_NETWORK = "1" from a clean TMPDIR after fetch.
  S5  Acquire here (A7): nvidia-ml-py (PyPI sdist sha256), cupy, cuda-python
      (licence characterised from its tree).

ITEMS
  19a Tune: telemetry daemon at 1 Hz → bus frames; footer reads only from it;
      power-limit helper with a sudoers rule restricted to the NVML set call;
      kernel lab (NVRTC engine + 34-sample curriculum) packaged as
      symoneural-kernel-lab, tests run, results to receipts labelled measured.
  19b Remix per S2 in Symoneural-API/app/remix; tokens encrypted at rest under
      /etc/symoneural; Chat proposes, the API writes the playlist.
  19c FreeToken per S3; outcome recorded either way.
  19d API v1: /openapi.json exported to meta-symoneural/api/openapi-v1.json;
      conformance test fails the build on drift; CHANGELOG rule additive-only.
  19e Offline proof for packagegroup-symoneural-rack per S4; every network reach
      recorded as a defect and fixed in the recipe.
  19f TEMPLATECONF for meta-symoneural; a symonbuild launcher that sets the
      environment and invokes the pinned BitBake; regenerate the report; tag
      estate-v0.1 naming every phase commit.

GATE: 19e passes for every shipped recipe; 19d green; footer agrees with
      nvidia-smi for 60 s; symonbuild builds the rack; tag placed (no remote).
COMMIT: "phase 19: Tune on the bus; Remix on the Web API; FreeToken outcome; API v1 frozen; offline proof; symonbuild; estate-v0.1"
RETURN
  ACQUIRED three: tag → SHA, licences as read
  TUNE fields and agreement; power round trip; kernel tests passed / total
  REMIX OAuth round-trip, playlist written, or "spotify.env unset — unit off"
  FABRIC RUNS / DEFERRED (evidence);  API openapi-v1 sha256, conformance green
  OFFLINE proven / total, reaches fixed;  ESTATE symonbuild works, tag SHA
  DECISIONS FOR GARRETT: none
```

---

*After Phase 19: the Swift client, generated from `openapi-v1.json` in Xcode. Ask the advisor for that prompt when the tag lands.*
