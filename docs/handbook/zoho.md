# Zoho — Directory, SSO, and the wider suite

## Why Zoho is the IdP

Zoho One is already the identity spine (`one.zoho.com` appears in the
`symoneural.com` SPF record). Zoho is **not** in Anthropic's built-in provider
list, so the integration is **Custom SAML**.

## SSO — what is DONE

- Application created in Zoho Directory
- **Issuer** and **ACS URL** matched — `YtgXgNBn2yIWMIIadbpBgincL`
- **NameID format:** Email Address
- **Application Username:** Primary email address
- **Attribute mapping:** `email` / `firstName` / `lastName`

## SSO — COMPLETE (13 September 2026)

All three remaining steps closed, in this order:

1. **Configure SSO** — Manual configuration, values taken from Zoho's own metadata
   (`Claude.xml`, saved to `~/Desktop/zoho/`). Anthropic reports **Connection
   activated**: Custom SAML, domain `symoneural.com`, X.509 valid
   **Sep 12 2026 → Sep 12 2029**.
2. **Assign Users** — Claude app now shows **3 Member(s)**, all Active:
   `symonsayadmin@`, `gmcdonald@`, `bhesley@`.
3. **Test** — org checklist reports SSO complete.

### Four things learned doing it, so they are not re-learned

**The ordering trap.** Anthropic's step 3 asks for three values that Zoho does not
produce until Zoho's own "Set up SSO" step is finished. Sitting on step 3 with
nothing to paste is the symptom of the Zoho side being incomplete, not a missing
field on the Anthropic page.

**Zoho publishes no metadata URL.** Dynamic configuration cannot work. Verified by
fetching every candidate: `/sso/metadata` returns 200 but `text/html` (a login
page), `/metadata` and `/sso/metadata.xml` both 404. Zoho gives a **downloadable
file** instead. Use Manual.

**The Entity ID and the SSO URL are the same string.** Both are
`https://directory.zoho.com/p/938948405/app/1353981000000004007/sso`. It looks
like a copy-paste error and is not. The logout endpoint is that URL plus
`/logout` — do not use it here.

**There is no Zoho user ID to map to `id`.** The metadata declares exactly one
NameID format, `emailAddress`, and no attributes. In Zoho's Attribute Mapping the
**Attribute Name is free text** (you type `id`) while the **Attribute Value is a
fixed dropdown**. The dropdown offers First name, Last name, Email ID Prefix,
Primary email address, Full name, Employee Id, Designation, Department, Reporting
To, Work Location, Country Code, Date of Birth — no ZUID. Map `id` to **Primary
email address**, the same value as `email`; Anthropic's step 4 sanctions exactly
this. Not *Email ID Prefix* (drops the domain) and not *Employee Id* (unpopulated,
and an empty required attribute fails login in a way that looks like a config
error).

Final mapping: `firstName`→First name, `lastName`→Last name, `email`→Primary email
address, `id`→Primary email address.

**Consequence accepted:** identity is tied to the email address, so changing
someone's email reads as a new user. Fine at three people.

**`groups` was skipped** — Zoho's picker exposes user profile fields only. Sign-in
works; roles are assigned by hand in Claude.

## Two things that are settled

**Cloudflare is not involved in SSO.** The domain is already Verified. See
`cloudflare.md` — the Cloudflare work is Phase 15's tunnel and is unrelated.

**Rotate the org invite link.** It appeared in a screenshot, auto-approves any
`@symoneural.com` address, and is valid to 28 Oct 2026. The ⟳ beside the copy
button. This is the one item here with an active exposure attached.

## NOT STARTED — the rest of Zoho

You asked for *"all zoho features, apps, connectors."* Recorded, not built. Zoho
Desk and Zoho Projects both appear as available connectors but **neither is
authenticated**. Scope only — see `docs/SCOPE-NOT-STARTED.md`.
