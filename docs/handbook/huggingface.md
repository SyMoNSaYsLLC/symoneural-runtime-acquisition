# Hugging Face — and the weights policy

## The rule, first

**Weights never enter git.** No exceptions, no formats, no "just this small one."
GGUF, safetensors, `.bin`, `.pt` — none of it. The repo is source and recipes.

`tools/pre-publish-audit.sh` scans for weights before any push precisely because
this rule is easy to break by accident.

## Status: connector NOT authenticated

A Hugging Face connector is available but **has not been authenticated**. No
token exists on this machine for it.

## What matters when weights do get pulled

### The model card is authoritative, not the GitHub repo

For any DeepSeek-class model this bites immediately:

| Repo | Code licence | **Weights licence** |
|---|---|---|
| DeepSeek-R1 | MIT | **MIT** — README §7 covers weights explicitly |
| DeepSeek-V3.2-Exp | MIT | MIT |
| DeepSeek-V3 | MIT (`LICENSE-CODE`) | **DeepSeek Model License v1.0** — use-based restrictions, not OSI |

GitHub reports V3 as MIT because it detects `LICENSE-CODE` and **misses**
`LICENSE-MODEL`. Two files, two licences, and the scanner reads the wrong one.

**R1's distilled variants are not uniformly MIT either** — the Llama-8B/70B
distills stay under Meta's Llama licence (700M-MAU clause, acceptable-use policy,
naming requirements); the Qwen-2.5-derived distills are Apache-2.0.

### Rebranding GGUF

`gguf_new_metadata.py` rewrites `general.name`. That is the correct and only
field to touch.

**Never rewrite `general.architecture`.** It tells the loader how to interpret
the tensors. Changing it produces a file that loads and then generates garbage —
a failure that looks like a model quality problem and is actually a metadata lie.

### git-lfs

Some HF repos require `git-lfs`. It is **MISSING** on this machine. Install it
before any HF clone, or you will get pointer files instead of weights and not
notice until load time.

## NOT STARTED

No model has been acquired into this estate. The model set has been
characterised, but characterisation is not acquisition — R16 applies.
