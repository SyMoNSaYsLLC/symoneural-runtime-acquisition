# symoneural-awcc — AWCC (Alienware Command Center for Linux) in the Platform runtime

Status vocabulary: PASS / FAIL / BLOCKED / NOT TESTED / NOT STARTED. Every row below is a verified
fact with its evidence or an explicit status. Results are in section 6; nothing here is inferred.

## 1. Ruling and scope

Garrett, 2026-09-14: "we need to add this to our build" … "you can do the awcc". Recorded in
`acquisition/pending-acquisitions.json` (row `AWCC`) and `provider-decisions.json` (`awcc`,
SYMONEURAL-OWNED): AWCC is built as a **separate GPL-3.0 executable** in its own package and
process, never linked into proprietary or native estate libraries, GPL obligations preserved (the
complete corresponding source is the committed, verified tree; the `-src` package carries the
debug sources), no relabelling. It is the same licence class as kawpowminer, which stays DEFERRED;
the ruling here covers AWCC only.

What AWCC is: the unofficial Alienware / Dell G-series control tool — thermal and fan modes,
G-mode, lighting — as a root daemon (`awcc -d`), a CLI and an ImGui/GLFW/OpenGL GUI. It talks to
firmware through the **acpi_call** out-of-tree kernel module (`/proc/acpi/call`) and to lighting
devices over USB (vendor 187c). Neither is part of this work (section 5).

## 2. Sources (SOURCES-100, all VERIFIED from HEAD)

| Component | Upstream | Pin | Licence (file) | Role |
|---|---|---|---|---|
| `AWCC` | gh:tr1xem/AWCC | v1.19.0 = `0ec42c4b3ddc3c4e412ad69353cd251e1f348280` (lightweight tag) | GPL-3.0 (`LICENSE` md5 `641dd5661bc2…`) | the application |
| `loguru` | gh:emilk/loguru | v2.2.0 → `ba2240d19bae…` (tag object `2702212f…`) | public-domain style (`LICENSE`) | logging, compiled in |
| `json` | gh:nlohmann/json | v3.12.0 → `55f93686c015…` | MIT | header-only; same commit as pytorch's vendored copy |
| `glfw` | gh:glfw/glfw | 3.5.1 → `d9d6f0f1f967…` | Zlib | window/GL context, static, X11 backend |
| `imgui` | gh:ocornut/imgui | v1.92.9b = `f1cc2ae15e53…` | MIT | GUI toolkit, compiled in (no docking API used) |
| `libusb-cmake` | gh:libusb/libusb-cmake | v1.0.30-0 → `c8477c10ac2a…` | LGPL-2.1 (libusb sources vendored in the tree) | USB access, static |
| `stb` | gh:nothings/stb | master head `2c980bb59875…` (no upstream tags) | MIT / Unlicense | `stb_image.h` |

Upstream's `CMakeLists.txt` pins every one of the six to a MOVING branch (`master` / `main`,
`GIT_SHALLOW`). The estate records the commit actually used and refuses to fetch at configure time.
Each tree lives at `Symoneural-Platform/src/alienware/source/<component>/`, pin store in
`Symoneural-Platform/src/alienware/.gitpins/` (local), acquired through `tools/ingest-and-commit`
(one commit each, `f3ecc4f8c` … `d9add47bf`).

## 3. How the build stays offline and unpatched

| Upstream mechanism | Estate answer | Where |
|---|---|---|
| `FetchContent_Declare(… GIT_REPOSITORY … GIT_TAG master)` ×6 | `symoneural-pristine` **`SYMON_DEP_TREES`** exports each pinned tree from `HEAD:<source_path>` into `${WORKDIR}/deps/<name>` after `tools/ingest-tree verify <component>`; the recipe passes `FETCHCONTENT_FULLY_DISCONNECTED=ON` and `FETCHCONTENT_SOURCE_DIR_<NAME>` for each | class (additive, default empty), recipe |
| `ExternalProject_Add(libevdev GIT_REPOSITORY gitlab…)` + meson | a recipe-carried **`ExternalProject.cmake` shadow** first on `CMAKE_MODULE_PATH`: includes the real module, turns the `libevdev` project into an empty target whose `_EP_SOURCE_DIR`/`_EP_BINARY_DIR` point at the sysroot (`usr/include/libevdev-1.0`, `usr/lib/libevdev.a`); any other ExternalProject is a FATAL_ERROR | `recipes-platform/symoneural-awcc/files/ExternalProject.cmake` |
| static `libevdev.a` expected | oe-core `libevdev` 1.13.7 built shared **and** static in the Platform estate build (`EXTRA_OEMESON:append:pn-libevdev = " -Ddefault_library=both"`) | `conf/templates/platform-estate/local.conf.sample` |
| `find_package(OpenGL)` | oe-core **`libglvnd`** (vendor-neutral dispatch) via `DISTRO_FEATURES:append = " opengl glvnd"` — no mesa/LLVM build; rendering needs a vendor GL at run time | template |
| `find_package(X11)`, GLFW X11 backend | oe-core X11 libraries; `GLFW_BUILD_WAYLAND=OFF`, `GLFW_BUILD_X11=ON` for the baseline | recipe |
| GLFW `dlopen`s its X11 libraries | explicit `RDEPENDS` on libx11, libxrandr, libxinerama, libxcursor, libxi, libxrender, libxext (shlib detection cannot see dlopen) | recipe |
| `libusb` install rules | `LIBUSB_INSTALL_TARGETS=OFF` (the archive is linked into awcc, nothing else ships) | recipe |
| build paths from `${WORKDIR}/deps` in `__FILE__`/DWARF | class adds `-ffile-prefix-map=${SYMON_DEPS_DIR}=${TARGET_DBGSRC_DIR}/deps` when dependency trees are declared (first build: 57 such strings failed buildpaths QA) | class |

No file of any acquired tree is modified; `do_patch` stays `noexec`.

## 4. First meaningful failures and fixes (build 1 → 3)

1. `ExternalProject_Get_Property: External project "libevdev" has no source_dir` — CMake 4.4 stores
   the directories as upper-case `_EP_SOURCE_DIR` / `_EP_BINARY_DIR`; the shadow set lower-case names.
2. `buildpaths` QA: `/usr/bin/awcc` contained `${WORKDIR}/deps/{glfw,libusb,json,imgui,loguru,stb}`
   paths (57 strings) — OE's prefix maps cover `${S}`, `${B}` and the sysroots, not the dependency
   exports. Fixed in the class, never by INSANE_SKIP.
3. Staged install: the Platform feed lacked `libc6`, `libglvnd`, `libudev1` … because only explicitly
   built recipes write packages; fixed by building with `--runall=package_write_ipk`. The same proof
   showed the package's `Depends` naming no X11 library → explicit `RDEPENDS` (GLFW dlopen).

## 5. Boundaries recorded, not provided

| Item | Status |
|---|---|
| `acpi_call` kernel module (`/proc/acpi/call`; Debian package `acpi-call-dkms`) | NOT ACQUIRED — a further out-of-tree module for the Platform runtime, both kernel targets, same pattern as the NVIDIA modules |
| Alienware USB lighting devices (vendor 187c), a display and a vendor GL library | not present in the qemux86-64 baseline; daemon, GUI and device control NOT TESTED |
| Debian-profile `.deb` for the development machine | NOT STARTED (needs the Debian X11/GL/udev development closure pinned by sha256, as the NVIDIA Debian target did for kernel inputs) |
| Reproducibility | NOT TESTED |
| Upstream `project(VERSION 1.17.0)` while the tag is v1.19.0 | recorded; the binary reports the CMake define |

## 6. Results

See `generated/evidence/platform/AWCC-BUILD.txt` (build identity, packages, control, files) and
`generated/evidence/platform/AWCC-PROOF.txt` (`tools/awcc-proof`: disposable root installed by the
estate's opkg from an indexed copy of the Platform feed, NEEDED closure inside the root through the
root's own loader, `awcc --version` and `awcc --help` with an empty environment, leakage checks).
The matrix row is kept in `generated/ORIGINALS-BY-RUNTIME.md` (Platform section).
