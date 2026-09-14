# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/ml/source/scikit-learn"

LICENSE = "BSD-3-Clause"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
# Four entries REMOVED, and the reason is a property of the class rather than a
# licensing judgement: scikit-learn's .gitattributes marks build_tools (and
# benchmarks, asv_benchmarks, maint_tools, .*) as EXPORT-IGNORE, so
# `git archive HEAD` correctly omits them and they can NEVER be present in the
# pristine export. Declaring them made do_unpack fail permanently:
#   LIC_FILES_CHKSUM names 4 file(s) absent from the export:
#   build_tools/wheels/LICENSE_{linux,macos,windows}.txt, check_license.py
# They are licence texts for libraries bundled into upstream's BINARY WHEELS
# (cibuildwheel tooling). SyMoNeuRaL does not build or ship those wheels, so
# they cover nothing we distribute. Removing them narrows the declaration to
# what the export actually contains - it does not discard applicable terms.
# NOTE: an export is NOT always a full copy of the worktree. mpmath has no
# export-ignore and matched exactly (248 == 248 == 248), which is what made
# "exports are complete" look like a general rule. It is not.
LIC_FILES_CHKSUM = "file://COPYING;md5=bdb6f7facb161e909d9554c4dba7e3d5 \
                    file://sklearn/externals/array_api_compat/LICENSE;md5=3d4ab4243dc36b64cb5d45edfcff7242 \
                    file://sklearn/externals/array_api_extra/LICENSE;md5=88200d470f94211ec903b46e40b5c09b \
                    file://sklearn/svm/src/liblinear/COPYRIGHT;md5=4baf47a10698d8d50aa7907b77be55e9"

SRC_URI = "git://github.com/scikit-learn/scikit-learn;protocol=https;branch=1.9.X"

# Modify these as desired
PV = "1.9.1"
SRCREV = "866c0f51e7560ef0303cbcc5f159df5382ea9e3f"

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
inherit pkgconfig python_mesonpy






# --- SYMONEURAL BUILD DEPS ---------------------------------------------------
# D2: scikit-learn builds against the numpy and scipy SyMoNeuRaL ships, not
# OE-Core's python3-numpy.
DEPENDS += "symoneural-cython-native symoneural-numpy-native symoneural-numpy symoneural-scipy python3"

# pyproject-build validates [build-system] requires against the NATIVE interpreter
# even under --no-isolation, and reports:
#   Unmet dependencies (checked against .../recipe-sysroot-native/usr/bin/nativepython3):
#     scipy<1.19.0,>=1.10.0   found: not installed
# scipy IS provided - it is in DEPENDS above and staged into the TARGET sysroot,
# where a cross-compiled extension actually needs it. The check looks in the
# native environment, which is the wrong place for a cross build; there is no
# symoneural-scipy-native and building one would mean compiling scipy twice to
# satisfy a check rather than a consumer.
#
# Same reasoning and same flag as symoneural-scipy uses for pythran: the
# dependency is declared and genuinely supplied, the validator is looking in the
# wrong sysroot. Skipping is honest here; it would not be if scipy were absent.
PEP517_BUILD_OPTS += "--skip-dependency-check"

# scikit-learn's Cython sources CIMPORT scipy's declarations:
#   sklearn/utils/_cython_blas.pyx:3: 'scipy/linalg/cython_blas.pxd' not found
# That is the real reason the build wanted scipy "installed" natively - it needs
# scipy's .pxd HEADERS, not just a version number.
#
# scipy is staged into the TARGET sysroot (correct - that is where its compiled
# extensions belong), but Cython runs NATIVELY and resolves cimports against the
# native interpreter's path. The headers are therefore invisible to it.
#
# Injecting an include path is not available: scikit-learn hardcodes cython_args
# in sklearn/meson.build with no meson option to extend it, so EXTRA_OEMESON
# cannot reach it.
#
# So mirror the declarations into the native sysroot. Only *.pxd and *.pxi - 12
# files, pure Cython declaration text, architecture-INDEPENDENT. No compiled
# extension and no target .so crosses into the native environment, which is the
# thing that must not happen and is why this is not a blanket copy of
# site-packages.
#
# NOT symoneural-scipy-native: that would compile the whole of scipy a second
# time, natively, to satisfy a header lookup. Same cost as the real build for no
# additional artifact.
# NOTE: no $(( )) arithmetic anywhere below. BitBake parses $( as its own
# expansion and dies with "NotImplementedError: $((" before the shell ever sees
# it. Counting is done with wc -l instead.
do_configure:prepend() {
    tgt="${STAGING_LIBDIR}/${PYTHON_DIR}/site-packages"
    nat="${STAGING_LIBDIR_NATIVE}/${PYTHON_DIR}/site-packages"
    if [ ! -d "$tgt/scipy" ]; then
        bbfatal "scipy not staged in the target sysroot - check DEPENDS"
    fi
    cd "$tgt" || bbfatal "cannot enter $tgt"
    find scipy \( -name '*.pxd' -o -name '*.pxi' \) -print > "${WORKDIR}/.pxd-list"
    while read -r f; do
        install -d "$nat/`dirname "$f"`"
        install -m 0644 "$tgt/$f" "$nat/$f"
    done < "${WORKDIR}/.pxd-list"
    # Cython needs each directory to resolve as a package on the path.
    find "$nat/scipy" -type d -print > "${WORKDIR}/.pxd-dirs" 2>/dev/null || true
    while read -r d; do
        [ -e "$d/__init__.py" ] || : > "$d/__init__.py"
    done < "${WORKDIR}/.pxd-dirs"
    bbnote "mirrored `wc -l < ${WORKDIR}/.pxd-list` scipy .pxd/.pxi declarations into the native sysroot"
}

# Runtime edges read from this wheel's dist-info METADATA Requires-Dist (estate-provided
# distributions). OE does not derive RDEPENDS from wheel metadata; the recipe must.
# Checked by tools/check-python-runtime-closures.py.
RDEPENDS:${PN} += "symoneural-numpy symoneural-scipy"
# Runtime edges to the acquired distributions (wheel METADATA, target 3.14, no extras).
RDEPENDS:${PN} += "symoneural-joblib symoneural-narwhals symoneural-threadpoolctl"
