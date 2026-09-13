# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/numerics/source/numpy"

LICENSE = "BSD-3-Clause"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
# Three of recipetool's generated entries were removed:
#   vendored-meson/meson/test cases/common/42 subproject/mylicense.txt
#   vendored-meson/meson/test cases/common/42 subproject/subprojects/sublib/sublicense1.txt
#   vendored-meson/meson/test cases/common/42 subproject/subprojects/sublib/sublicense2.txt
# Two independent reasons. Structurally, LIC_FILES_CHKSUM is WHITESPACE-SEPARATED
# and those paths contain spaces - that is what broke do_populate_lic.
# Semantically, md5=d41d8cd9... is the md5 of an EMPTY FILE: they are Meson test
# fixtures, not licence documents.
LIC_FILES_CHKSUM = "file://.spin/LICENSE;md5=bde96408b6df910d3d7c40d3d9a10d31 \
                    file://LICENSE.txt;md5=26080bf81b2662c7119d3ef28ae197fd \
                    file://doc/source/_static/scipy-mathjax/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
                    file://doc/source/license.rst;md5=04c3984c770a5a9fed6ccc47f2d2b515 \
                    file://numpy/_build_utils/tempita/LICENSE.txt;md5=a0fff136e7abb00075d7bd1e9a1ecd71 \
                    file://numpy/_core/include/numpy/libdivide/LICENSE.txt;md5=e1c97b70a98c8ec5aff0aa275fdb2c91 \
                    file://numpy/_core/src/common/pythoncapi-compat/COPYING;md5=f74f54822fab8814a50330e4e4578b88 \
                    file://numpy/_core/src/highway/LICENSE;md5=e583f1fc1c22da0f388b23a31df5b591 \
                    file://numpy/_core/src/highway/debian/copyright;md5=0090ea7383ac2a23a7e6b5532e4ae5c6 \
                    file://numpy/_core/src/multiarray/dragon4_LICENSE.txt;md5=d82ecc7c1dc5709b559fe3ef67b4d73a \
                    file://numpy/_core/src/npysort/x86-simd-sort/LICENSE.md;md5=32e4087908578b334f5b91fce7a470a0 \
                    file://numpy/_core/src/umath/svml/LICENSE;md5=54d69368f84829557fb97f5e81ab3b64 \
                    file://numpy/fft/pocketfft/LICENSE.md;md5=bb0e49a83ba802d32f3a05a7b8b2180b \
                    file://numpy/linalg/lapack_lite/LICENSE.txt;md5=7d9f3a90a3f3d41052b70a31c1daf8ad \
                    file://numpy/ma/LICENSE;md5=560a44ba225da50f5d488426818c8474 \
                    file://numpy/random/LICENSE.md;md5=09b2aa3c0d32aea36fb330dc9c728fc4 \
                    file://numpy/random/src/distributions/LICENSE.md;md5=0a26f80d7361a8d65d2f8daf8c7e3de8 \
                    file://numpy/random/src/mt19937/LICENSE.md;md5=58535013375c548c899f1d5b80a0e886 \
                    file://numpy/random/src/pcg64/LICENSE.md;md5=5d0d131c837b97f368c758589b4e82f0 \
                    file://numpy/random/src/philox/LICENSE.md;md5=d1f2eb63cadd62578bd54c4a7f20f03e \
                    file://numpy/random/src/sfc64/LICENSE.md;md5=ad204ac84919852ee6d8e4154dddca08 \
                    file://numpy/random/src/splitmix64/LICENSE.md;md5=aed2fe30600fb0e72efc56b188d9e0df \
                    file://vendored-meson/meson/COPYING;md5=3b83ef96387f14655fc854ddc3c6bd57 \
                    file://vendored-meson/meson/docs/markdown/legal.md;md5=000fe0dead3c0d575839e9d2bcfe2d5e \
                    file://vendored-meson/meson/packaging/License.rtf;md5=074ef868ead2735d006e564c24e059c7"
SRC_URI = "gitsm://github.com/numpy/numpy;protocol=https;branch=maintenance/2.5.x"

# Modify these as desired
PV = "2.5.3"
SRCREV = "dd88c0c19b54ad9ed3533224221285bf0873249a"

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
# Mirrors OE-Core's own python3-numpy_2.5.3 (identical upstream version, known to
# cross-build): pkgconfig is what lets meson's Cython link test find target python3,
# and cython.bbclass supplies python3-cython-native plus metadata stripping.
inherit pkgconfig python_mesonpy

# NOT `inherit cython`. That class is INCOMPATIBLE with externalsrc: its
# do_compile postfunc strip_cython_metadata runs `sed -i` over every .c/.cpp
# under ${S}, and with externalsrc ${S} IS the pristine upstream tree. It
# changed no content but rewrote files and stripped the exec bit from
# numpy/_core/src/umath/loops_hyperbolic.dispatch.cpp.src - a real mutation of
# acquired source. We take only what was actually needed from it:
DEPENDS += "python3-cython-native"



# NOTE: no Makefile found, unable to determine what needs to be done





# --- packaging hygiene -------------------------------------------------------
# numpy records its build configuration into __config__.py, which embeds TMPDIR
# and the build-host HOME. OE-Core's own recipe fixes this by sed-ing
# ${S}/numpy/__config__.py.in during do_patch - i.e. by editing the SOURCE.
# We build from a pristine externalsrc tree that must never be modified, so the
# same correction is applied to the INSTALLED artifact instead. Same outcome,
# source left untouched.
do_install:append() {
    for f in ${D}${PYTHON_SITEPACKAGES_DIR}/numpy/__config__.py; do
        [ -f "$f" ] || continue
        sed -i -e 's|${TMPDIR}|/build|g' -e 's|${HOME}|/build|g' \
               -e 's|${WORKDIR}|/build|g' -e 's|${S}|/source|g' "$f"
    done
    # drop the stale bytecode so it cannot carry the paths we just stripped
    rm -f ${D}${PYTHON_SITEPACKAGES_DIR}/numpy/__pycache__/__config__.*.pyc
}

# numpy ships static helper libraries (libnpymath.a, libnpyrandom.a) inside the
# python package tree. They belong in -staticdev, not the runtime package.
FILES:${PN}-staticdev += "${PYTHON_SITEPACKAGES_DIR}/numpy/_core/lib/*.a \
                          ${PYTHON_SITEPACKAGES_DIR}/numpy/random/lib/*.a"

# scipy and scikit-learn need numpy importable by nativepython3 at build time.
# D2 says they build against the numpy SyMoNeuRaL ships, so we provide a native
# variant rather than pulling OE-Core python3-numpy into the build.
BBCLASSEXTEND = "native"
