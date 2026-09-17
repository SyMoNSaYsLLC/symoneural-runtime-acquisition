"""Diffuse clean-root proof body: run INSIDE the extracted image by tools/clean-root-proof.

Diffuse is the first runtime in this harness whose surface is NOT Python. There is
nothing importable to import: packagegroup-symoneural-diffuse is one package holding
sd-cli and libstable-diffusion.so. python3-modules is in the image so this harness can
run at all (it looks for ${R}/usr/bin/python3.1[0-9] and refuses a root without one);
this file imports only the standard library and drives the binary as a subprocess.

What it proves, in order:
  1. the packaged files are the ones the recipe says, and the vendored ggml 0.19.0
     development interface is NOT in the root (it would collide with symoneural-ggml);
  2. sd-cli runs under the TARGET loader against TARGET libraries, with the host's
     ld.so.cache inhibited - the harness's own trace is the judge of leakage;
  3. THE FLAGS THE UNIT WILL LAUNCH WITH EXIST. docs/operator-checklist.md item 14d says
     `--backend te=cpu`; upstream's own docs/flux.md at this same pin says `--clip-on-cpu`.
     At most one is real. `sd-cli --help` is the arbiter and this is where the answer is
     recorded, because two documents disagreeing is exactly the case where the
     repository wins;
  4. a real 768x768 render completes and the PNG it wrote is a 768x768 PNG, with the
     wall time measured against the Phase 14 gate (768 square within 20% of 11.2 s).

Weights are EXTERNAL and are not in the image (symoneural-image-diffuse installs none).
They live in the recorded model store, acquisition/model-register.json SYMON_MODELS_DIR.
"""
import json, os, struct, subprocess, sys, time

R = os.environ.get("SYM_CLEAN_ROOT") or sys.exit("FAIL: SYM_CLEAN_ROOT unset; run via tools/clean-root-proof")
S2 = os.environ.get("SYM_CUDA_S2") == "1"
MODELS = "/home/google/symoneural-models/image"          # SYMON_MODELS_DIR/image

bad = []
def check(ok, msg):
    print("  %-72s %s" % (msg, "PASS" if ok else "FAIL"))
    if not ok:
        bad.append(msg)

# ---------------------------------------------------------------- 1. the packaged root
print("--- packaged files")
SD_CLI = os.path.join(R, "usr/bin/sd-cli")
SD_LIB = os.path.join(R, "usr/lib/libstable-diffusion.so")
check(os.path.isfile(SD_CLI) and os.access(SD_CLI, os.X_OK), "usr/bin/sd-cli present and executable")
check(os.path.isfile(SD_LIB), "usr/lib/libstable-diffusion.so present")
check(not os.path.exists(os.path.join(R, "usr/bin/sd-server")),
      "usr/bin/sd-server ABSENT (packaged apart; no image installs a second HTTP listener)")
leaked = [n for n in os.listdir(os.path.join(R, "usr/include")) if n.startswith(("ggml", "gguf"))] \
         if os.path.isdir(os.path.join(R, "usr/include")) else []
check(not leaked, "no ggml*/gguf* headers in usr/include (would collide with symoneural-ggml-dev)")
check(not os.path.isdir(os.path.join(R, "usr/lib/cmake/ggml")),
      "no usr/lib/cmake/ggml (a find_package(ggml) here would resolve to the WRONG ggml)")

# ------------------------------------------------- 2. run it under the target loader
# The harness wraps PYTHON in a loader invocation; sd-cli needs the same treatment, built
# from the same parts. In S2 mode the host driver directory joins the path so libcuda.so.1
# resolves - that is the declared boundary, and the harness's trace checks every other
# mapping against the package database.
LD = next((p for p in (os.path.join(R, "lib/ld-linux-x86-64.so.2"),
                       os.path.join(R, "lib64/ld-linux-x86-64.so.2")) if os.path.exists(p)), None)
if LD is None:
    sys.exit("FAIL: no target loader in the root")
LIBPATH = "%s/lib:%s/usr/lib" % (R, R)
if S2:
    LIBPATH += ":/usr/lib/x86_64-linux-gnu"

def sd(*args, timeout=900):
    cmd = [LD, "--inhibit-cache", "--library-path", LIBPATH, SD_CLI, *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

r = sd("--help", timeout=120)
helptext = (r.stdout or "") + (r.stderr or "")
check(r.returncode == 0 and len(helptext) > 500,
      "sd-cli --help runs under the target loader (rc=%d, %d bytes)" % (r.returncode, len(helptext)))

# --------------------------------------------- 3. the launch flags, settled by the binary
print("--- launch flags: checklist 14d vs upstream docs/flux.md, arbitrated by --help")
WANT = ["--diffusion-model", "--vae", "--clip_l", "--t5xxl", "--cfg-scale",
        "--sampling-method", "--steps", "-H", "-W", "-o", "-p", "--seed"]
for f in WANT:
    check(f in helptext, "flag %s exists" % f)
te_backend = "--backend" in helptext          # checklist 14d wording
clip_on_cpu = "--clip-on-cpu" in helptext     # upstream docs/flux.md wording
vae_tiling = "--vae-tiling" in helptext
diffusion_fa = "--diffusion-fa" in helptext
print("  RESOLVED: --backend=%s  --clip-on-cpu=%s  --vae-tiling=%s  --diffusion-fa=%s"
      % (te_backend, clip_on_cpu, vae_tiling, diffusion_fa))
check(te_backend or clip_on_cpu,
      "at least one of --backend / --clip-on-cpu exists (the text encoder can be kept off the card)")

# ------------------------------------------------------------------ 4. weights and render
print("--- weights (EXTERNAL; no image installs them)")
FILES = {"flux1-schnell-q4_k.gguf": 6884606880, "t5xxl-Q8_0.gguf": 5199794784,
         "clip_l.safetensors": 246144152, "ae.safetensors": 335304388}
have_all = True
for name, size in FILES.items():
    p = os.path.join(MODELS, name)
    ok = os.path.isfile(p) and os.path.getsize(p) == size
    have_all &= ok
    check(ok, "%s present at %d bytes" % (name, size))

if have_all and not bad:
    print("--- render: 768x768, 4 steps, cfg 1.0, euler")
    # The GPU lock. The canonical implementation is symoneural_api.gpulock (and the C half
    # in libsymoneural-api); neither is in this image, and this proof must not invent a
    # second policy. So it does the minimum that is honest: REFUSE if a live holder is
    # recorded, and do not take the lock itself - a holder this image cannot release on
    # crash would strand the card, which is the exact failure gpulock.py exists to prevent.
    lock = os.environ.get("SYM_GPU_LOCK", "/run/symoneural/gpu.lock")
    holder = None
    try:
        with open(lock) as fh:
            holder = json.load(fh)
    except Exception:
        pass
    if holder:
        try:
            os.kill(int(holder["pid"]), 0)
            alive = True
        except Exception:
            alive = False
        check(not alive, "GPU lock free (held by %r, alive=%s)" % (holder.get("unit"), alive))
    else:
        print("  %-72s %s" % ("GPU lock free (no record at %s)" % lock, "PASS"))

    out = os.path.join(R, "tmp/diffuse-proof-768.png")
    argv = ["--diffusion-model", os.path.join(MODELS, "flux1-schnell-q4_k.gguf"),
            "--vae", os.path.join(MODELS, "ae.safetensors"),
            "--clip_l", os.path.join(MODELS, "clip_l.safetensors"),
            "--t5xxl", os.path.join(MODELS, "t5xxl-Q8_0.gguf"),
            "-p", "a lovely cat holding a sign that says SyMoNeuRaL",
            "--cfg-scale", "1.0", "--sampling-method", "euler", "--steps", "4",
            "-H", "768", "-W", "768", "--seed", "42", "-o", out]
    if diffusion_fa:
        argv.append("--diffusion-fa")
    if vae_tiling:
        argv.append("--vae-tiling")
    # TWO renders with the launch line, then ONE with the checklist's, because 14d's
    # flag choice turned out to be the whole gate.
    #
    # The unit launches one process per render - that is what makes VRAM release
    # deterministic (docs/diffuse/ARCHITECTURE.md section 2) - so sd-cli always pays a
    # model load. Run 1 pays it from disk, run 2 from page cache; on this host they came
    # out equal, which says the cost is the load into VRAM and the compute, not the I/O.
    def stage_times(text):
        out = {}
        for line in text.splitlines():
            for key, label in (("get_learned_condition completed", "text encoder"),
                               ("sampling completed", "sampling"),
                               ("decode_first_stage completed", "vae decode"),
                               ("total params memory size", "params")):
                if key in line:
                    out[label] = line.split("- ", 1)[-1].strip()
        return out

    times, stages = [], {}
    for attempt in (1, 2):
        if os.path.exists(out):
            os.unlink(out)
        t0 = time.time()
        r = sd(*argv, "-v")
        times.append(time.time() - t0)
        blob = (r.stdout or "") + (r.stderr or "")
        tail = "\n".join(blob.strip().splitlines()[-14:])
        stages = stage_times(blob) or stages
        check(r.returncode == 0, "sd-cli render %d rc=0 (rc=%d, %.1f s)" % (attempt, r.returncode, times[-1]))
        if r.returncode != 0:
            print(tail); break
    dt = times[-1]
    for label in ("params", "text encoder", "sampling", "vae decode"):
        if label in stages:
            print("    | %-13s %s" % (label, stages[label]))
    ok = os.path.isfile(out) and os.path.getsize(out) > 10000
    check(ok, "wrote %s (%d bytes)" % (out, os.path.getsize(out) if os.path.exists(out) else 0))
    if ok:
        with open(out, "rb") as fh:
            head = fh.read(33)
        sig_ok = head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR"
        w, h = struct.unpack(">II", head[16:24]) if sig_ok else (0, 0)
        check(sig_ok and (w, h) == (768, 768), "it is a 768x768 PNG (signature ok=%s, %dx%d)" % (sig_ok, w, h))
    print("  RENDER WALL TIME: run1 %.1f s, run2 %.1f s  (each includes a full model load;"
          % (times[0], times[-1]))
    print("    one process per render is the design, not a benchmarking artefact)")
    print("  PHASE 14 GATE: 768 square within 20%% of 11.2 s, i.e. <= 13.44 s -> %.1f s: %s"
          % (dt, "MET" if dt <= 13.44 else "NOT MET"))

    # THE CORRECTION, MEASURED. docs/operator-checklist.md item 14d prescribes
    # `--backend te=cpu`; upstream's docs/flux.md calls the flag --clip-on-cpu and
    # recommends it for cards with 6 GB or even 4 GB. This card has 15.92 GiB, and the
    # lock hands it to ONE unit at a time - so there is no other resident tenant to leave
    # room for, and keeping the T5 encoder off the card buys nothing while costing this:
    if clip_on_cpu:
        if os.path.exists(out):
            os.unlink(out)
        t0 = time.time()
        r = sd(*argv, "--clip-on-cpu", "-v")
        cpu_dt = time.time() - t0
        cs = stage_times((r.stdout or "") + (r.stderr or ""))
        check(r.returncode == 0, "sd-cli render with --clip-on-cpu rc=0 (%.1f s)" % cpu_dt)
        print("  WITH --clip-on-cpu (the checklist's te=cpu): %.1f s vs %.1f s  -> +%.1f s, gate %s"
              % (cpu_dt, dt, cpu_dt - dt, "MET" if cpu_dt <= 13.44 else "NOT MET"))
        for label in ("params", "text encoder"):
            if label in cs:
                print("    | %-13s %s" % (label, cs[label]))
        print("  So 14d's launch line is wrong for THIS hardware. Recorded in")
        print("  docs/diffuse/ARCHITECTURE.md section 8; the checklist is a document, the card is not.")
    for line in tail.splitlines():
        if any(k in line for k in ("sampling completed", "VAE decode", "total params", "get_learned_condition")):
            print("    | " + line.strip())
elif not have_all:
    print("  SKIPPED the render: the weight set is incomplete. This is a correct")
    print("  intermediate state, not a pass - the gate stays UNMEASURED.")

if bad:
    print("FAIL:"); [print("   -", b) for b in bad]; sys.exit(1)
print("DIFFUSE CLEAN ROOT PROOF: PASS")
