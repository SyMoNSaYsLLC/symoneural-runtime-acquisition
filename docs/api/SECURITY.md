# Symoneural-API security invariants

- **No arbitrary command execution.** The native supervisor takes `argv` and
  `execv`s; there is no `run_shell`, `system()`, `shell=True` or `/bin/sh -c`
  interface in C or Python. Remaining deviation: `rack.c` uses `popen()` for a
  fixed `nvidia-smi` query (no untrusted data) — scheduled for `posix_spawn`.
- **No client-provided executable or model paths.** Unit executables come from
  the registry/service definitions; models from the model register.
- **Secrets never in git, never in diagnostics.** Tokens are read from
  provisioned environment variables (`symoneural-secrets`, `/etc/symoneural`,
  R13); comparison is `hmac.compare_digest`; missing means unconfigured and
  fails closed. `symoneural-api-util` prints paths and states, never values.
  Native errors carry a status and message, not filesystem paths.
- **Route classes are explicit.** Every route has exactly one class; an
  unclassified route is a bug. OPERATOR_ONLY answers 404 to non-operators.
- **Public demos are a separate trust boundary.** `DemoPolicy` restricts models,
  units, mutations, rate, concurrency, session lifetime and tools;
  `expose_admin` is fixed false and rejected at registration. Browser-visible
  descriptors contain no paths, secrets or service names (tested).
- **No customer-specific logic in generic code** — asserted by
  `test_no_customer_name_in_generic_code` over the Python modules, C sources and
  headers.
- **Accounts, SMTP and application workflows stay in Python** (Phase 11-T);
  never in `libsymoneural-api`. Claude protocol parsing stays out of native LLM C.
