# PHASE 15 — Gateway and cutover: symoneural.com served entirely from the estate

## STATUS: PENDING — NOT STARTED

**starts after: Phase 14 gate**

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
so the phase is self-contained when picked up. Nothing acquired, built, deployed
or started. Per A7, none of the four sources below has been cloned: acquisition
happens only inside the phase that builds the component.


Milestone: the 522 goes away through a tunnel; every process behind it traces to
a pin.

---

## SETTLED

- **S1** Tunnel posture, outbound only.
- **S2** Caddy for static and compression; **FastAPI does all routing**.
- **S3** Authentication before public (the accounts service from 11-T).
- **S4** Acquire here (A7): `caddy`, `cloudflared`, `tronpy`, `coincurve`.
  Wrangler is consumed as the **PUBLISHED `wrangler@4.131.1` npm package via
  npmsw** (kind **PACKAGE** in the manifest, `MIT OR Apache-2.0`), paired to
  workerd `v1.20260911.1`; the workers-sdk tree stays **REFERENCE-ONLY**.
- **OUT OF SCOPE BY RULE:** account tiers and pricing — *never invent pricing*.
- `TUNNEL_TOKEN` is set (manifest); public hostnames on tunnel
  `symoneural-estate` may not yet exist — if the named tunnel connects but no
  hostname routes, report **"public hostnames not configured"** and stop at the
  quick-tunnel proof.

## ITEMS

- **15a** `caddy` and `cloudflared` via the go classes with **tracked module
  closures**; `symon-gateway` via cargo; `limiter.go` → wasm with `GOOS=wasip1`
  so the gateway leaves native-fallback.
- **15b** Caddyfile in `meta-symoneural`: August's routing intent; `servers` block
  with `trusted_proxies` for the tunnel's local peer and `client_ip_headers
  CF-Connecting-IP`; **spoofed `X-Forwarded-For` test proves the limiter keys on
  the real client**.
- **15c** Accounts required on `/api/chat`, `/api/image`, `/api/remix` per 11-T
  scopes; `/api/status` and `/demo/dispatchos.html` public.
- **15d** Site generators in `Symoneural-UI/app/` emit pages reading the bus;
  `manifest.json`, brand icons, service worker caching the shell and **never**
  `/api`; deploy to `/var/www/symoneural`.
- **15e** SBOM for every recipe in `packagegroup-symoneural-rack`; `cve-check`;
  both on `/receipts`.
- **15f** Quick tunnel (`cloudflared tunnel --url http://127.0.0.1:80`) reached
  from a second network. Named tunnel: `TUNNEL_TOKEN` from the manifest →
  cloudflared service; report Healthy / hostnames routed or not. Once Healthy,
  the old locally-configured tunnel `symoneural` and any leftover cloudflared
  service or `~/.cloudflared/*.json` on the box are **recorded for removal**
  (**removal is a Garrett action; do not delete**).

## GATE

Quick tunnel live with chat streaming; 15b spoof test passes; SBOM and cve-check
on `/receipts`; named tunnel Healthy or the exact reason reported.

## COMMIT

`phase 15: gateway stack from the estate; tunnel; auth on public surfaces; SBOM on receipts`

## RETURN

- ACQUIRED four: tag → SHA, licence files, collisions
- BUILT caddy / cloudflared / symon-gateway / limiter.wasm
- EDGE quick tunnel reached YES/NO; named tunnel Healthy / hostnames routed YES/NO
- AUTH endpoints gated; SBOM recipes covered, CVEs by severity
- DECISIONS FOR GARRETT: none

---

## NOTES CARRIED IN FROM EARLIER PHASES

**`TUNNEL_TOKEN` is `set`** — confirmed reading `/etc/symoneural/manifest.json`
in Phase 10 (names and status only, no values). The manifest's
`units_that_stay_off_until_set` lists it as gating "named Cloudflare tunnel (quick
tunnel still works)", and since it is set, the named tunnel is not held off. The
four keys that ARE unset (`SYM_GATEWAY_BENEFICIARY`, `SYM_GATEWAY_CONTRACT`,
`SYM_MINER_POOL`, `SYM_MINER_WALLET`) gate TRON licensing and real mining, not
this phase.

**workers-sdk was recorded REFERENCE-ONLY in Phase 10**, which is what S4's
wrangler-as-PACKAGE decision rests on. Reason recorded verbatim there: *"pnpm
catalog: protocol unsupported by npm / OE npm class"* — evidence
`npm error code EUNSUPPORTEDPROTOCOL / Unsupported URL Type "catalog:":
catalog:default`. The tree stays acquired and pinned; only the source build is
declined.

**workerd is pinned at v1.20260911.1**, matching S4. Confirmed in Phase 10 when
the PV sweep derived `1.20260911.1` from the tag at its SRCREV, which also
confirms the SRCREV advance to the release decision landed.

**npmsw:// is proven working in this estate** as of Phase 10: two recipes
(`symoneural-anthropic-sdk-typescript`, `symoneural-hlsjs`) ship a
`npm-shrinkwrap.json` beside the recipe and fetch through it, with the lockfile
generated inside a disposable export so R1 is never relaxed. S4's wrangler
approach uses the same mechanism.

**R14 applies throughout:** `127.0.0.1:8800` is read-only — never stopped,
restarted, edited or redeployed. 15f's removal of the old tunnel is explicitly a
Garrett action; this phase records, it does not delete.
