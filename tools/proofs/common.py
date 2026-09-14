"""Common clean-root proof body: run INSIDE the extracted image by tools/clean-root-proof.

Imports the Torch + Transformers runtime closure (every symoneural-* distribution the
Common image ships), evaluates every consumer's declared Requires-Dist against the
versions actually installed, refuses build frontends, and drives one representative
consumer path end to end: a tokenizer trained in-process (tokenizers, Rust) wrapped as a
transformers fast tokenizer, feeding a transformers model built from a config (no
weights) that runs a forward pass on torch, whose output round-trips through
safetensors. NOTHING here touches the network: HF_HUB_OFFLINE and TRANSFORMERS_OFFLINE
are set before any import, and the proof asserts that a hub download attempt is
refused rather than tried.
"""
import io, os, sys, importlib
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "2"
from importlib.metadata import version, requires, PackageNotFoundError

# see tools/proofs/ravencalc.py: let anything that spawns re-enter the TARGET interpreter
_wrap = os.environ.get("SYM_TARGET_PYTHON")
if _wrap and os.path.exists(_wrap):
    import multiprocessing
    sys.executable = _wrap
    multiprocessing.set_executable(_wrap)

bad = []

# --- 0. the install record. IMAGE_FEATURES is empty, so OE removes /var/lib/opkg from
# the rootfs (no package-management feature); the deploy manifest written by do_rootfs
# is the record of what opkg installed. opkg status is used only if a root carries it.
installed = {}
status = os.environ.get("SYM_OPKG_STATUS")
if status and os.path.exists(status):
    pkg, st = None, None
    for line in open(status, encoding="utf-8", errors="replace"):
        if line.startswith("Package: "): pkg = line.split(": ", 1)[1].strip()
        elif line.startswith("Status: "): st = line.split(": ", 1)[1].strip()
        elif line.strip() == "" and pkg: installed[pkg] = st; pkg, st = None, None
    if pkg: installed[pkg] = st
    record = "opkg status"
else:
    mani = os.environ.get("SYM_IMAGE_MANIFEST", "")
    for line in open(mani, encoding="utf-8") if mani and os.path.exists(mani) else []:
        parts = line.split()
        if len(parts) >= 3: installed[parts[0]] = parts[2]
    record = "deploy manifest" if installed else "NONE"
sym = sorted(p for p in installed if p.startswith("symoneural-"))
print("  install record: %s -> %d packages, %d symoneural-*" % (record, len(installed), len(sym)))
if not installed: bad.append("no install record: neither opkg status nor SYM_IMAGE_MANIFEST")
for need in ("symoneural-pytorch", "symoneural-transformers", "symoneural-setuptools",
             "symoneural-networkx", "symoneural-jinja2", "symoneural-markupsafe"):
    if need not in installed: bad.append("%s not in the install record" % need)

# --- 0b. a clean runtime carries no build frontend. Checked BEFORE anything imports
# setuptools: setuptools 84 puts its own _vendor/ on sys.path once imported, and a
# vendored wheel/packaging then resolves - that is setuptools' private copy, not a
# shipped distribution, and is asserted as such below. setuptools itself is NOT on this
# list: torch 2.14 declares setuptools>=77.0.3 as a RUNTIME requirement
# (torch.utils.cpp_extension imports it), so the estate ships its own copy for torch.
assert "setuptools" not in sys.modules
for f in ("maturin", "hatchling", "pdm", "flit_core", "setuptools_scm", "build", "wheel", "pip"):
    try:
        importlib.import_module(f); bad.append("build frontend %s present on target" % f)
    except Exception:
        pass

# --- 1. every distribution of the closure imports; module -> distribution name
want = {"torch": "torch", "transformers": "transformers", "huggingface_hub": "huggingface-hub",
        "tokenizers": "tokenizers", "safetensors": "safetensors", "numpy": "numpy",
        "filelock": "filelock", "fsspec": "fsspec", "hf_xet": "hf-xet", "packaging": "packaging",
        "yaml": "PyYAML", "tqdm": "tqdm", "typer": "typer", "rich": "rich", "pygments": "Pygments",
        "markdown_it": "markdown-it-py", "mdurl": "mdurl", "shellingham": "shellingham",
        "regex": "regex", "jinja2": "Jinja2", "markupsafe": "MarkupSafe", "networkx": "networkx",
        "setuptools": "setuptools", "sympy": "sympy", "mpmath": "mpmath",
        "typing_extensions": "typing_extensions", "click": "click", "httpx": "httpx",
        "annotated_doc": "annotated-doc"}
# shipped only when the packagegroup carries accelerate (see its recipe: BLOCKED on torch USE_DISTRIBUTED)
HAS_ACCELERATE = "symoneural-accelerate" in installed
if HAS_ACCELERATE:
    want.update({"accelerate": "accelerate", "psutil": "psutil"})
ver = {}
for mod, dist in want.items():
    try:
        importlib.import_module(mod)
    except Exception as e:
        bad.append("%s: import failed: %r" % (mod, e)); print("  %-20s FAIL %r" % (mod, e)); continue
    try:
        ver[dist] = version(dist)
    except PackageNotFoundError:
        ver[dist] = "?"
    print("  %-20s %s" % (mod, ver[dist]))

# --- 2. after the imports above, setuptools' path hook is live: whatever `wheel` now
# resolves to must be setuptools' private vendored copy and nothing else.
import setuptools
try:
    import wheel as _w
    if "/setuptools/_vendor/" not in _w.__file__:
        bad.append("a non-vendored wheel is installed: %s" % _w.__file__)
    else:
        print("  wheel resolves only via setuptools/_vendor (setuptools' private copy; no wheel distribution shipped)")
except Exception:
    pass
site = [p for p in sys.path if p.endswith("site-packages")]
for sp in site:
    for f in ("wheel", "pip", "maturin", "hatchling", "flit_core"):
        if os.path.exists(os.path.join(sp, f)): bad.append("top-level %s/ present in %s" % (f, sp))

# --- 3. the declared closure is the gate: every consumer's Requires-Dist, evaluated for
# this target and this set of extras (none selected), against what is installed.
from packaging.requirements import Requirement
from packaging.version import Version
checked = 0
for consumer in ("torch", "transformers", "huggingface-hub", "tokenizers", "typer", "rich",
                 "markdown-it-py", "Jinja2", "sympy", "safetensors") + (("accelerate",) if HAS_ACCELERATE else ()):
    for r in requires(consumer) or []:
        req = Requirement(r)
        if req.marker is not None and not req.marker.evaluate({"extra": ""}):
            continue
        name = req.name.lower().replace("_", "-")
        try:
            got = version(req.name)
        except PackageNotFoundError:
            bad.append("%s requires %s: NOT INSTALLED" % (consumer, r)); continue
        checked += 1
        if req.specifier and not req.specifier.contains(Version(got), prereleases=True):
            bad.append("%s requires %s but %s is installed" % (consumer, r, got))
print("  declared closure: %d runtime requirements evaluated against installed versions" % checked)

if not bad:
    import numpy as np, torch
    torch.set_num_threads(2)
    torch.manual_seed(0)

    # torch: linear algebra against a numpy reference, and autograd
    a = torch.randn(64, 32); b = torch.randn(32, 16)
    assert np.allclose((a @ b).numpy(), a.numpy() @ b.numpy(), atol=1e-4)
    x = torch.randn(8, requires_grad=True); (x ** 2).sum().backward()
    assert torch.allclose(x.grad, 2 * x)
    # torch's declared runtime edges are LIVE imports, not metadata only:
    import torch.utils.cpp_extension                      # imports setuptools at module load
    assert "setuptools" in sys.modules
    import torch.fx
    class Tiny(torch.nn.Module):
        def __init__(self): super().__init__(); self.l = torch.nn.Linear(4, 2)
        def forward(self, t): return torch.relu(self.l(t))
    traced = torch.fx.symbolic_trace(Tiny())
    assert len(list(traced.graph.nodes)) >= 4, list(traced.graph.nodes)

    # tokenizers (Rust): train BPE in-process from an iterator, no files, no network
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    tok = Tokenizer(models.BPE(unk_token="[UNK]"))
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    corpus = ["symoneural builds its runtimes from pristine upstream source",
              "bitbake packages every wheel from a pinned tree", "the estate ships what it owns"] * 20
    tok.train_from_iterator(corpus, trainers.BpeTrainer(vocab_size=200, special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]"]))
    enc = tok.encode("symoneural ships pristine runtimes")
    assert tok.decode(enc.ids).replace(" ", "") == "symoneuralshipspristineruntimes", tok.decode(enc.ids)

    # transformers (offline): fast tokenizer wrapping the trained one -> model from CONFIG
    # (no weights, no hub) -> forward pass on torch
    import transformers
    from transformers import BertConfig, BertModel, PreTrainedTokenizerFast
    # offline mode as the libraries themselves see it: hub constant read at import, and
    # transformers' own probe where this version exposes one (5.x moved it to utils.hub)
    import huggingface_hub.constants as _hc
    assert _hc.HF_HUB_OFFLINE, "HF_HUB_OFFLINE not honoured by huggingface_hub"
    _probe = getattr(getattr(transformers.utils, "hub", None), "is_offline_mode", None) \
        or getattr(transformers.utils, "is_offline_mode", None)
    if _probe is not None:
        assert _probe(), "transformers does not report offline mode"
    ptok = PreTrainedTokenizerFast(tokenizer_object=tok, unk_token="[UNK]", cls_token="[CLS]",
                                   sep_token="[SEP]", pad_token="[PAD]")
    batch = ptok(["symoneural ships pristine runtimes", "the estate ships what it owns"],
                 padding=True, return_tensors="pt")
    cfg = BertConfig(vocab_size=tok.get_vocab_size(), hidden_size=32, num_hidden_layers=2,
                     num_attention_heads=4, intermediate_size=64, max_position_embeddings=64)
    model = BertModel(cfg).eval()
    with torch.no_grad():
        out = model(**batch).last_hidden_state
    assert out.shape == (2, batch["input_ids"].shape[1], 32), out.shape
    assert torch.isfinite(out).all()

    # safetensors: the model's state round-trips through the Rust serialiser
    from safetensors.torch import save_file, load_file
    sf = os.path.join(os.environ.get("TMPDIR", "/tmp"), "proof.safetensors")
    save_file(model.state_dict(), sf)
    back = load_file(sf)
    assert all(torch.equal(back[k], v) for k, v in model.state_dict().items())
    os.unlink(sf)

    # accelerate: only when the image ships it. On a torch built USE_DISTRIBUTED=0 this
    # block FAILS at Accelerator.prepare() (utils/other.py model_has_dtensor imports
    # torch.distributed.tensor); that failure is the evidence recorded in its recipe.
    accel_note = "not shipped in this image (BLOCKED on torch USE_DISTRIBUTED=0; see symoneural-accelerate recipe)"
    if HAS_ACCELERATE:
        import psutil
        assert psutil.Process().pid == os.getpid() and psutil.cpu_count() >= 1
        from accelerate import Accelerator
        from accelerate.utils import set_seed
        set_seed(0)
        acc = Accelerator(cpu=True)
        net = torch.nn.Linear(4, 1); opt = torch.optim.SGD(net.parameters(), lr=0.1)
        data = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(torch.randn(16, 4), torch.randn(16, 1)), batch_size=8)
        net, opt, data = acc.prepare(net, opt, data)
        before = net.weight.detach().clone()
        for xb, yb in data:
            loss = torch.nn.functional.mse_loss(net(xb), yb)
            acc.backward(loss); opt.step(); opt.zero_grad()
        assert torch.isfinite(loss) and not torch.equal(before, net.weight.detach()), "no optimisation step took effect"
        assert acc.gather(torch.tensor([acc.process_index])).tolist() == [0]
        assert str(acc.device) == "cpu"
        accel_note = "Accelerator(cpu) prepared model/optimizer/dataloader and one SGD epoch changed the weights, gather ok; psutil read this process"

    # huggingface_hub: offline mode REFUSES a download rather than attempting one
    import huggingface_hub
    from huggingface_hub.errors import OfflineModeIsEnabled, LocalEntryNotFoundError
    try:
        huggingface_hub.hf_hub_download("symoneural/does-not-exist", "config.json")
        raise AssertionError("hf_hub_download proceeded in offline mode")
    except (OfflineModeIsEnabled, LocalEntryNotFoundError) as e:
        # 1.x wraps the refusal in LocalEntryNotFoundError; the CAUSE must be the offline
        # guard, i.e. the request was refused before any connection was attempted
        cause = e if isinstance(e, OfflineModeIsEnabled) else e.__cause__
        assert isinstance(cause, OfflineModeIsEnabled), "hub call failed for a reason other than the offline guard: %r" % (cause,)
    assert huggingface_hub.hf_hub_url("org/repo", "f.bin").endswith("/org/repo/resolve/main/f.bin")

    # hf_xet (Rust) is loaded and reports its version
    import hf_xet
    assert hasattr(hf_xet, "__version__") or hasattr(hf_xet, "download_files")

    # pyyaml through libyaml, regex Unicode properties, filelock, fsspec, tqdm, packaging
    import yaml
    assert yaml.__with_libyaml__, "PyYAML built without libyaml bindings"
    doc = {"runtime": "Common", "packages": sym[:3]}
    assert yaml.load(yaml.dump(doc, Dumper=yaml.CDumper), Loader=yaml.CLoader) == doc
    import regex
    assert regex.match(r"\p{Greek}+", "αβγ").group() == "αβγ"
    from filelock import FileLock
    lk = FileLock(os.path.join(os.environ.get("TMPDIR", "/tmp"), "proof.lock"))
    with lk: assert lk.is_locked
    assert not lk.is_locked
    import fsspec
    fs = fsspec.filesystem("file"); p = os.path.join(os.environ.get("TMPDIR", "/tmp"), "fsspec.txt")
    with fs.open(p, "w") as fh: fh.write("owned")
    assert fs.cat(p) == b"owned"; fs.rm(p)
    from tqdm import tqdm
    assert sum(tqdm(range(10), file=io.StringIO())) == 45
    from packaging.version import Version as V
    assert V(ver["torch"]) >= V("2.14.0a0") and V("2.14.0a0+gitunknown").local == "gitunknown"

    # typer -> click, rich -> pygments/markdown-it-py/mdurl, shellingham
    import typer
    from typer.testing import CliRunner
    app = typer.Typer()
    @app.command()
    def hello(unit: str): typer.echo("unit=%s" % unit)
    res = CliRunner().invoke(app, ["common"])
    assert res.exit_code == 0 and "unit=common" in res.output, res.output
    from rich.console import Console
    from rich.table import Table
    buf = io.StringIO(); con = Console(file=buf, width=60, force_terminal=False)
    t = Table("package", "version"); t.add_row("torch", ver["torch"]); con.print(t)
    assert "torch" in buf.getvalue() and ver["torch"] in buf.getvalue()
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import TerminalFormatter
    assert "import" in highlight("import torch", PythonLexer(), TerminalFormatter())
    from markdown_it import MarkdownIt
    html = MarkdownIt().render("# Common\n\n[hub](https://huggingface.co/x)")
    assert "<h1>Common</h1>" in html and 'href="https://huggingface.co/x"' in html, html
    import shellingham
    try:
        shellingham.detect_shell(); shell_note = "detected"
    except shellingham.ShellDetectionFailure:
        shell_note = "ShellDetectionFailure (expected: no shell parent under env -i)"

    # jinja2 -> markupsafe (C speedups), networkx
    import jinja2, markupsafe
    # MarkupSafe 3 defines escape() in Python and delegates the hot path to
    # _escape_inner, which must be the C extension's (the _speedups .so was built and
    # loaded), not the pure-python fallback in _native.py
    import markupsafe._speedups
    assert markupsafe._escape_inner.__module__ == "markupsafe._speedups", markupsafe._escape_inner.__module__
    assert jinja2.Template("{{ n | e }}:{{ items | length }}").render(n="<b>", items=[1, 2]) == "&lt;b&gt;:2"
    import networkx as nx
    g = nx.Graph([(1, 2), (2, 3), (3, 4), (1, 4)])
    assert nx.shortest_path(g, 1, 3) in ([1, 2, 3], [1, 4, 3])

    print("  meaningful ops PASS: torch matmul == numpy reference and autograd grad == 2x; "
          "torch.utils.cpp_extension imported setuptools at load (live runtime edge); torch.fx "
          "traced a module; tokenizers trained BPE in-process (Rust) and round-tripped; "
          "transformers PreTrainedTokenizerFast wrapped it and BertModel(config) ran a forward "
          "pass -> %s; safetensors round-tripped the state_dict; accelerate: %s; huggingface_hub refused a "
          "download under HF_HUB_OFFLINE; hf_xet loaded; PyYAML via libyaml; regex \\p{Greek}; "
          "filelock; fsspec local fs; tqdm; packaging; typer CliRunner exit 0; rich table; "
          "pygments; markdown-it-py rendered a link; shellingham %s; jinja2 escaped through "
          "markupsafe._speedups; networkx shortest_path"
          % (tuple(out.shape), accel_note, shell_note))
    print("  NO NETWORK: offline mode asserted before import; the one hub call made was "
          "proven to be refused; no model weights were fetched or present.")

if bad:
    print("FAIL:"); [print("   -", b) for b in bad]; sys.exit(1)
print("COMMON CLEAN ROOT PROOF: PASS")
