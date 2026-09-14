# PyTorch `do_package_qa [buildpaths]` — root cause and correction

Recorded 2026-09-14. Recipe: `meta-symoneural/recipes-common/symoneural-pytorch/symoneural-pytorch_git.bb`.
Failing run's log: `.../symoneural-pytorch/2.14.0/temp/log.do_package_qa.3226883`.

## The failure

`bitbake symoneural-pytorch` reached `do_package_write_ipk` but failed
`do_package_qa` with 6 QA errors plus the fatal summary — 3 files, each reported
twice (TMPDIR and build-host HOME):

```
/usr/lib/python3.14/site-packages/torch/include/caffe2/core/macros.h   (symoneural-pytorch)
/usr/lib/python3.14/site-packages/torch/lib/libtorch_cpu.so            (symoneural-pytorch)
/usr/lib/python3.14/site-packages/torch/lib/.debug/libtorch_cpu.so     (symoneural-pytorch-dbg)
```

These are **two independent defects at two different layers**.

## Why no exemption was available

`openembedded-core/meta/classes-global/insane.bbclass`, `package_qa_check_buildpaths`:

```python
tmpdir = bytes(d.getVar('TMPDIR'), encoding="utf-8")
homedir = bytes(os.environ.get('HOME', ''), encoding="utf-8")
buildpaths_skip = (d.getVar("OEQA_BUILDPATHS_SKIP") or "").split()
with open(path, 'rb') as f:
    file_content = f.read()
    if tmpdir in file_content:
        oe.qa.handle_error("buildpaths", "... contains reference to TMPDIR", d)
    if homedir and homedir in file_content and not any(path.startswith(homedir.decode()) for path in buildpaths_skip):
        oe.qa.handle_error("buildpaths", "... build host HOME directory ...", d)
```

`OEQA_BUILDPATHS_SKIP` — the remedy the QA message itself advertises — gates
**only the HOME branch**. The TMPDIR test is unconditional. Setting it would
have cleared at most 3 of the 6 errors and the task would still have failed.
The only exemption that could pass is `INSANE_SKIP += "buildpaths"`, which
would mask a real reproducibility defect. So the paths were removed instead.

## Defect A — `CAFFE2_BUILD_STRINGS`

`cmake/Codegen.cmake:46-48` runs an unconditional `configure_file()` on
`caffe2/core/macros.h.in`. Lines 33-52 of that template expand two CMake
variables verbatim:

```
{"CXX_COMPILER", R"PYT(${CMAKE_CXX_COMPILER})PYT"}, \
{"CXX_FLAGS",    R"PYT(${CMAKE_CXX_FLAGS})PYT"}, \
```

The compiler path is absolute (`<WORKDIR>/recipe-sysroot-native/usr/bin/...`),
and the flags string contains the *text* of OE's own `-ffile-prefix-map`
arguments, which necessarily name absolute paths. Those two strings are the
**only** two `/home/google` matches in the stripped, shipped `libtorch_cpu.so`
(`.rodata`, offsets 227462848 and 227463040), reaching it because macros.h is
`#include`d into a translation unit.

`-ffile-prefix-map` was **not** dropped by scikit-build-core or PyTorch's CMake.
The opposite: `DEBUG_PREFIX_MAP` → `CXXFLAGS` → `CMAKE_CXX_FLAGS` arrived intact
and works correctly on DWARF. Prefix-map flags transform `__FILE__` and debug
records; they cannot touch a CMake-expanded literal.

**Correction.** A CMake file injected through `CMAKE_PROJECT_torch_INCLUDE`
(`CMAKE_PROJECT_NAME:STATIC=torch`, read from the live `CMakeCache.txt`) uses
`cmake_language(DEFER CALL ...)` to rewrite the generated
`${CMAKE_BINARY_DIR}/caffe2/core/macros.h` at the end of top-level directory
processing — after `caffe2/CMakeLists.txt:2` has included `Codegen.cmake`, and
before the build step compiles anything. The build root is replaced by fixed
tokens, longest prefix first (`WORKDIR` → `/workdir`, `TMPDIR` → `/oe-tmpdir`,
`HOME` → `/build-host-home`), since WORKDIR lies under TMPDIR lies under HOME.
The hook `message(FATAL_ERROR ...)` if the header is absent or if any prefix
survives, so the correction cannot silently no-op.

These values are diagnostics returned by `caffe2::GetBuildOptions()`. Replacing
the build root keeps them readable and makes them byte-identical across build
roots, which is the reproducibility property that matters.

## Defect B — PeachPy `STT_FILE` symbols

The 12 matches in `.debug/libtorch_cpu.so` are **not DWARF**. Offset
`0x11caf2b2f` lies inside `.strtab` (`0x119934218` + `0x454c5ee`), and
`readelf --symbols` shows them as:

```
273578: 0000000000000000  0 FILE LOCAL DEFAULT ABS <WORKDIR>/pristine/third_party/NNPACK/src/x86_64-fma/2d-fourier-8x8.py
```

— 12 entries, all `third_party/NNPACK/src/x86_64-fma/*.py`.

`third_party/NNPACK/CMakeLists.txt:428-435` hands PeachPy an absolute path:

```cmake
COMMAND "PYTHONPATH=${PEACHPY_PYTHONPATH}"
  ${PYTHON_EXECUTABLE} -m peachpy.x86_64
    -mabi=sysv -g4 -mimage-format=${PEACHPY_IMAGE_FORMAT}
    -o ${obj} "${PROJECT_SOURCE_DIR}/${src}"
```

PeachPy is a Python assembler, not a compiler, so no GCC flag reaches it. It
stamps that argv string verbatim into a FILE symbol:
`peachpy/x86_64/__main__.py:243` → `peachpy/writer.py:128` → 
`peachpy/formats/elf/image.py:19-20` (`source_symbol.type = SymbolType.file;
source_symbol.name = source`). No `abspath` on that path — line 263 abspaths
only the *include* directories, which never reach the symbol.

**Correction.** `PYTHON_EXECUTABLE` is pointed at a generated wrapper that,
**only** when it sees `-m peachpy.x86_64`, re-expresses the trailing input
argument relative to `${S}` and runs from there; every other invocation
(including the `-c` probe `FindPythonInterp` issues) is passed straight through
by `exec`. If the input is not under `${S}` the wrapper refuses rather than
emitting a build path. `PYTHON_EXECUTABLE` has no consumer in PyTorch's own
`cmake/` — only `third_party/{NNPACK,pybind11,XNNPACK,composable_kernel}` — and
the wrapper delegates to the same interpreter `FindPythonInterp` previously
resolved (`recipe-sysroot-native/usr/bin/nativepython3`).

## Not modified

No acquired upstream source tree was touched. Both corrections live in the
recipe, which generates both hook files into `${WORKDIR}/symoneural-hooks/`
during `do_configure`.

## Separately recorded, still open

`log.do_compile:338` shows a real, executed, undeclared build-time network
fetch:

```
-- Downloading six (Python package) to <WORKDIR>/pristine/build/confu-srcs/six (define PYTHON_SIX_SOURCE_DIR to avoid it)
```

`cmake/External/nnpack.cmake:48` pre-defines `PYTHON_PEACHPY_SOURCE_DIR` from
the vendored tree, so PeachPy and opcodes are not fetched — only `six` is.
`NNPACK/CMakeLists.txt:151` guards on `IF(NOT DEFINED PYTHON_SIX_SOURCE_DIR)`,
and `recipe-sysroot-native/usr/lib/python3.14/site-packages/six.py` already
exists via `python3-six-native`. It is currently masked by the CMake cache
holding the downloaded path. Tracked as the NNPACK hidden-network item; proving
it requires a clean configure, not a cached one.

## Result — verified 2026-09-14

Rebuild: `tools/symonbake Symoneural-Common symoneural-pytorch`.

```
Tasks Summary: Attempted 2031 tasks of which 2020 didn't need to be rerun and all succeeded.
Summary: There were 5 WARNING messages.
```

No ERROR line and no failed task. The prior run was `Attempted 2029 ... 1 failed`
with `7 ERROR messages`.

`do_package_qa` (`temp/log.do_package_qa.3236281`): 0 ERROR lines, no
`[buildpaths]` lines.

Both hooks are observed firing in `temp/log.do_compile`:

```
271 : -- Found PythonInterp: <WORKDIR>/symoneural-hooks/peachpy-relative-path (found version "3.14.7")
1114: -- symoneural: build paths removed from <S>/build/caffe2/core/macros.h
```

The three previously-offending packaged files, tested with the exact
`insane.bbclass` predicate (raw bytes of TMPDIR / HOME in the file):

```
TMPDIR=False HOME=False     0.0 MB  .../torch/include/caffe2/core/macros.h
TMPDIR=False HOME=False   262.4 MB  .../torch/lib/libtorch_cpu.so
TMPDIR=False HOME=False  4796.7 MB  .../torch/lib/.debug/libtorch_cpu.so
```

Verified again by streaming out of the emitted package itself,
`symoneural-pytorch_2.14.0-r0_x86-64-v3.ipk` — both `macros.h` and
`libtorch_cpu.so` clean.

Packages emitted (2026-09-14 04:53):

```
   116143868  symoneural-pytorch_2.14.0-r0_x86-64-v3.ipk
    14700250  symoneural-pytorch-src_2.14.0-r0_x86-64-v3.ipk
  1704950314  symoneural-pytorch-dbg_2.14.0-r0_x86-64-v3.ipk
         656  symoneural-pytorch-dev_2.14.0-r0_x86-64-v3.ipk
```

The substituted values are fixed tokens, so they are byte-identical under any
build root — the property the QA check is a proxy for:

```
{"CXX_COMPILER", R"PYT(/workdir/recipe-sysroot-native/usr/bin/x86_64-oe-linux/x86_64-oe-linux-g++)PYT"}, \
{"CXX_FLAGS",    R"PYT(-O2 -g -fcanon-prefix-map  -ffile-prefix-map=/workdir/pristine=/usr/src/debug/... )PYT"}, \
```

All 12 PeachPy FILE symbols in the packaged `.debug` copy are now relative, and
now match the convention GCC already used for NNPACK's own C++ translation
unit:

```
NNPACK.cpp
third_party/NNPACK/src/x86_64-fma/2d-fourier-8x8.py
... 12 total
```

Gates run against this build:

| Gate | Result |
| --- | --- |
| `do_package_qa` | PASS — 0 ERROR, no `[buildpaths]` |
| emitted `.ipk` contents | PASS — TMPDIR and HOME absent |
| `tools/ingest-tree verify pytorch` | PASS — `2b3ec3482903`, 141210 files, LISTING-VERIFIED (65 submodules); no acquired source modified |
| `tools/check-native-linkage.py` | PASS |
| `tools/check-python-runtime-closures.py --runtime Symoneural-Common` | VACUOUS — reports PASS but examined 0 wheels, so it proves nothing here; Common's closure recipes are drafted and not yet applied |

Not claimed by this record: REPRODUCIBILITY PASS. This was an incremental
rebuild (`do_unpack` did not re-run, so `${S}/build` was reused). The
substituted values are build-root independent by construction, but a
from-scratch build under a different root has not been performed.
