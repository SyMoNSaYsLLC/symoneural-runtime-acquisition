# Cloudflare

## Status: NOT STARTED — and deliberately so

Cloudflare has **no role in SSO**. The `symoneural.com` domain is already
Verified with Anthropic, and Zoho is the IdP. If anyone suggests a Cloudflare
step to finish SSO, that is a wrong turn — see `zoho.md`.

## What Cloudflare is actually for here

**Phase 15 — the tunnel.** Exposing a SyMoNeuRaL service to the outside world
without opening a port on this machine. That phase has not started.

## Why it is not started yet

There is nothing stable to expose. The runtimes are still being built from
source; `:8801` (the Phase 11 service) does not exist yet, and `:8800` is a
**read-only demo-critical deployment that must not be touched** (R14 — never
stop, restart, edit or redeploy it).

A tunnel to a service that does not exist is a security surface with no product
behind it. The correct order is: build the service, prove it, *then* expose it.

## DNS facts on record

`symoneural.com` SPF references `one.zoho.com` — mail and identity are Zoho.
Do not repoint anything without checking that first; it is the same record the
IdP integration relies on.

## NOT STARTED — the rest

*"all cloudflare account features"* is recorded as scope in
`docs/SCOPE-NOT-STARTED.md`. Nothing has been configured. No API token has been
created, and none should be until there is a specific job for it.
