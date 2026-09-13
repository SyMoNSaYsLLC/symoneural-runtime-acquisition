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

## SSO — what REMAINS (3 steps)

**The ordering trap, because it has cost time twice.** Anthropic's step 3 asks for
three values that **Zoho does not produce until Zoho's own step 2 is finished**.
The Zoho app showed *"Custom app created — 0 out of 3 completed"*: assign users,
**configure SSO**, test. It is the middle one that prints the IdP Login URL,
Entity ID and certificate. Sitting on Anthropic's step 3 waiting for values is the
symptom of Zoho's step 2 not being done — not of a missing field.

Also: `YtgXgNBn2yIWMIIadbpBgincL` is the **SP** Issuer that went **into Zoho**.
It is not what Anthropic's step 3 wants. Pasting it there gives a signature
validation failure that reads like a certificate problem.

1. **Configure SSO** — finish Zoho's step 2, then paste Zoho's **IdP Login URL**,
   **IdP Entity ID** and **X.509 certificate** into Anthropic's step 3.
2. **Assign Users** in Zoho to the Claude application.
3. **Test SSO** — in a **clean browser profile**, before enabling JIT
   provisioning. Testing while already signed in proves nothing.

Enable JIT provisioning **only after** a clean-browser test passes. JIT plus a
misconfigured attribute map creates accounts you then have to clean up.

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
