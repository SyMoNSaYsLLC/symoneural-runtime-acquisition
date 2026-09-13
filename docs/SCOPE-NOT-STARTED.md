# SCOPE — described, NOT started

Recorded 2026-09-13 because Garrett described the total scope of work and the
failure pattern he named is real: *"the ai agent i work with almost gets done
bringing in my sources it goes crazy and starts doing things when i didnt want to
do anything."*

**Nothing in this file has been started. It is here so it is not forgotten, and
so it is not mistaken for work in progress.**

Current actual work: **Phase 11**, which is not finished. Sources are still being
pulled and the runtimes are not yet customised — Garrett has not yet described
how he wants them.

---

## Accounts and identity

- Four Claude accounts: `bhesley@`, `symonsayadmin@`, `gmcdonald@` (all
  `symoneural.com`), and `garrettmcdonald87@gmail.com`.
  **Already resolved, no work needed:** settings are NOT per-account.
  `claude_desktop_config.json` carries no account or org key — one file serves
  all four, so they cannot desync. Sessions are per account (4 UUID dirs);
  settings are not.
- Two GitHub accounts: `SyMoNSaYsLLC` and `gpmcdonald`.
- Zoho addresses: `symonsayadmin@` (primary), `saynoreply@`, `sayalert@`,
  `saysupport@`, plus `garrettmcdonald87@gmail.com` linked.
- Google: `garrettmcdonald87@gmail.com`, `gpmcdonald87@gmail.com`.

## Integrations named

GitHub MCP (both accounts) · Gmail · Zoho apps and connectors · Cloudflare
account features · Gemini Pro · ChatGPT Plus · Google AI Studio ·
`console.cloud.google.com` (project `my-linux-drive-500514`) · antigravity.

## Already configured, currently inert

`developer_settings.json` has third-party inference **already pointed at a local
gateway**:

```
inferenceProvider        gateway
inferenceGatewayBaseUrl  http://localhost:9001
inferenceGatewayAuthScheme bearer
inferenceGatewayApiKey   <a real bearer token — NOT in this repo>
```

**Nothing is listening on 9001.** The file is excluded from config snapshots
because the key is a live credential.

> **DO NOT wire the estate's inference into Claude Desktop.** An earlier note in
> this session suggested pointing Claude Desktop at the estate's `llama-server`
> once Phase 12 builds it, and called that "self-hosting". **That is backwards.**
> SyMoNeuRaL exists so Garrett owns the whole stack — his recipes, his pins, his
> DispatchOS, his inference, serving HIS customers on HIS hardware. The chat unit
> serves `/api/chat` on `:8801` for tenants. Pointing a third-party desktop app at
> it makes the estate a **backend for someone else's product**, which inverts the
> entire reason for building it from pristine source.
>
> This stale `inferenceProvider: gateway` setting is the same shape and is inert
> only because nothing listens on 9001. If Phase 12 ever brings a gateway up
> there, the desktop would start consuming the chat unit by default. That should
> be a deliberate decision, not an inherited one — and the default answer is no.

## The eventual product

A **sandbox layer** so a customer asking for an AI build on `symoneural.com`
receives immediately what DispatchOS currently takes weeks to produce. This is
Phase 11-T generalised — tenants provisioned on demand rather than by hand.

---

## Why this is a file and not a task list

Every item above is real and wanted. None of it is next. The estate is at Phase
11 of 19, scipy does not yet build, and the runtime composition has not been
described. Building integrations now would repeat the failure this file exists
to prevent.
