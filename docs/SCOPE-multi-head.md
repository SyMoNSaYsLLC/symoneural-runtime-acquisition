# SCOPE — the multi-head surface ("4-headed AI monster")

**Status: SCOPED, NOT BUILT.** Design captured 2026-09-13 from Garrett's
description. No code exists. Recorded so it is not re-derived, and so the two
problems below are decided deliberately rather than discovered mid-build.

---

## The concept

A customer logs in with whichever assistant accounts they hold. Each connected
account is a **head**. Ask one question, every connected head answers, and the
surface shows where they agree and where they do not.

- 1 head → an ordinary assistant
- 4 heads → four independent answers to the same question, with agreement marked

**The user only gets the heads they log in to.** Nothing is provided on their
behalf.

| Head | Whose credential | Availability |
|---|---|---|
| **Symon** | **SyMoNeuRaL's own runtime** | first-party — we provide it |
| Claude | the customer's | only if they connect it |
| ChatGPT | the customer's | only if they connect it |
| Gemini | the customer's | only if they connect it |

---

## Why this does NOT violate the product rule

The standing rule is that SyMoNeuRaL never routes its inference to a third-party
API as a shortcut. This design does not, and the distinction is worth stating
precisely because it is easy to drift across:

- **Forbidden:** we take a customer's question, send it to OpenAI, and present the
  answer as ours. That makes the estate a reseller and the runtimes decorative.
- **This design:** the customer connects *their own* accounts. We add a head we
  actually built — **Symon** — and provide the surface that compares them.

Symon is the only head SyMoNeuRaL supplies. That is the product. The others are
the customer's existing subscriptions, which they already pay for, and which they
authorise individually.

**Design consequence, deliberate:** if a customer connects zero third-party
accounts, they still get Symon. The product must be worth using with one head.

---

## ONE SESSION — and the fork it creates

All four heads share **one session**: the same conversation, each seeing what the
others have said. Not four isolated chats stitched together afterwards.
`tools/modelbus` already implements exactly this — one append-only transcript that
every participant reads in full.

### The fork: does a head see the others BEFORE it answers?

This is the most consequential design decision in the whole surface, and the two
options are not interchangeable.

| | Blind round | Shared round |
|---|---|---|
| Each head sees | only the question | the question **and** other heads' answers |
| When they agree it means | **independent confirmation** | possibly just **anchoring** |
| Failure mode | four confidently wrong answers, no cross-check | one head's error propagates and the rest ratify it |
| Feels like | a panel of experts polled separately | a meeting where the first speaker sets the frame |

**Agreement is only evidence when the answers were independent.** If Gemini reads
Claude's answer first and then agrees, that agreement carries almost no
information — and the surface would display it identically to genuine independent
confirmation. That is a lie by interface.

### Recommended: blind first round, then shared discussion

1. **Round 1 — blind.** The question goes to every head. No head sees another.
   Agreement computed here is real, and this is the round the agreement badge
   reports on.
2. **Round 2 onward — shared.** Every head now sees the full transcript and may
   revise, object, or explain. This is where the "all models know what is going
   on" property lives.
3. **The badge never moves off round 1.** Later convergence is shown as discussion,
   never as confirmation.

That preserves both properties Garrett asked for — independent cross-checking
*and* a shared session — without one quietly destroying the value of the other.

## THE BLOCKER — verified, not assumed

**The estate serves nothing right now.**

```
ss -ltn | grep -E ':(8000|8800|8801)'   ->   no listeners
```

There is no API to add a surface to. Phase 11 has not produced `:8801`, and
`:8800` is the read-only demo that must not be touched. scipy's `do_compile` is
still failing, which blocks RavenCalc 6/6, which is the Phase 11 gate.

**Nothing of this can be built before that.** A backend surface on a backend that
does not run is the R16 failure in its purest form — it would be declared done and
never executed.

Ordering, and it is structural rather than a preference:

```
Phase 11  RavenCalc live on :8801, API answering      <- BLOCKED on scipy
Phase 12  models register; Chat live under the lock   <- needs 11
   then   multi-head surface                          <- needs a live API + a live Symon
```

---

## THE HARD PART — custody of other people's credentials

This is the real risk, and it is not a coding problem.

To call a customer's Claude/ChatGPT/Gemini account, the estate must **hold a
credential belonging to that customer**. That changes what this repository is:
today it holds no third-party user secrets at all.

Questions that must be answered before any code:

1. **OAuth or API keys?** OAuth is revocable by the user and never exposes a
   long-lived secret — strongly preferred. API keys are simpler and far worse:
   a pasted key is a bearer token with no expiry that we then own.
2. **Where do tokens live?** Not in `/etc/symoneural` — that is *our* secrets,
   not customers'. A per-tenant encrypted store, keyed per user, is a new
   component with its own threat model.
3. **What happens on breach?** Holding N customers' assistant credentials makes
   this box a target it is not currently. Blast radius must be sized first.
4. **Do the providers' terms permit it?** Server-side use of a consumer
   subscription on a user's behalf is restricted by some providers. **This is a
   terms question before it is an engineering question** and it can invalidate
   the whole design.

**Recommendation: settle 4 first.** If a provider forbids it, the head is
browser-side-only or does not exist, and that changes the architecture completely
— a client-side fan-out holds no credentials at all and sidesteps 1 through 3.

---

## What already exists and should be reused

**The route classification**, already designed for DispatchOS:

```
PUBLIC_BOOTSTRAP           /status - answers while the surface is off, no customer data
SHARED_AUTH                /login  - establishes identity; gating it makes entitlement unreachable
AUTHENTICATED_APPLICATION
ENTITLEMENT_REQUIRED
OPERATOR_ONLY
```

with the stated target: *accounts/auth = shared authentication authority;
customer→application mapping = shared entitlement authority.*

A head is an **entitlement**, not a new auth system. `ENTITLEMENT_REQUIRED` is
already the right class for "does this user have the Gemini head?"

**The accounts plumbing** is provisioned: `SYM_ACCOUNTS_ENABLED`,
`SYM_ACCOUNTS_SECRET`, `SYM_OWNER_EMAIL`, per-surface tokens.

**The comparison logic** is built and tested — `tools/modelbus`, carrying R-184's
rule forward: never decide who is right, never merge answers, preserve every
answer including the rejected one. The product surface must obey the same rule.
Showing a customer a merged "consensus answer" would be inventing an answer no
model gave.

---

## Decisions needed from Garrett

1. **Provider terms** — may a hosted service call a consumer subscription on a
   user's behalf? Answer before anything else.
2. **OAuth or keys**, given 1.
3. **Server-side fan-out or client-side?** Client-side holds no credentials and
   removes the entire custody problem, at the cost of no server-side history.
4. Does a **single-head** customer (Symon only) get the same surface, or a
   simpler one?
5. **Blind first round, or shared from the start?** The recommendation above is
   blind-then-shared. Shared-from-the-start is simpler to build and makes the
   agreement badge meaningless; that trade should be made knowingly.
