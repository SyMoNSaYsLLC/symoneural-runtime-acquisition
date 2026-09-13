# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/numerics/source/scipy"

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=6506a2e1578b1a1161d9bda0b896c647 \
                    file://LICENSES_bundled.txt;md5=fe2784111ff83b9451741c37b82985c6"
SRC_URI = "gitsm://github.com/scipy/scipy;protocol=https;branch=maintenance/1.18.x"

# Modify these as desired
PV = "1.18.1"
SRCREV = "e4e854eaa8f18d807cd3496028e257e36caa93cc"

inherit pkgconfig python_mesonpy


# WARNING: We were unable to map the following python package/module
# dependencies to the bitbake packages which include them:
#    Cython
#    numpy
#    pybind11
#    pythran

# WARNING: We were unable to map the following python package/module
# runtime dependencies to the bitbake packages which include them:
#    numpy

# --- SYMONEURAL BUILD DEPS ---------------------------------------------------
# pkgconfig is what lets meson's Cython link test find target python3 (the numpy
# pattern). NOT `inherit cython`: that class seds every .c/.cpp under ${S}, which
# under externalsrc is pristine acquired source.
#
# D2: scipy builds against symoneural-numpy, never OE-Core's python3-numpy.
# Building against a numpy we do not ship is precisely the provider collision
# the control plane exists to prevent.
# 11b DEPENDS. NOT gfortran-cross: it names no recipe in any layer
# (`find ~/symoneural-bootstrap-master -name 'gfortran*'` returns nothing) and
# bitbake refuses with "Nothing PROVIDES 'gfortran-cross'". None is needed - the
# cross toolchain already stages x86_64-oe-linux-gfortran into every target
# recipe-sysroot-native. Verified by invoking it directly:
#   GNU Fortran (GCC) 16.2.0 ; compiled a .f90 to a 2240-byte .o
# This is the THIRD item in a pasted spec naming something that does not exist,
# after pythran and python3-pythran-native.
#
# libgfortran IS required though - as its own recipe (libgfortran_16.2.bb), not
# via RUNTIMETARGET. Without it gfortran fails only WITH --sysroot:
#   fatal error: cannot read spec file 'libgfortran.spec'
# The 10a toolchain work is what put the compiler there:
# scipy's meson.build:91 previously died with
#   Unknown compiler(s): x86_64-oe-linux-gfortran
# because the cross toolchain was built LANGUAGES="c,c++" with FORTRAN="".
# symoneural.conf now carries FORTRAN:forcevariable = ",fortran".
# NOT python3-pythran-native: 11b names it, but it does not exist in ANY layer
# (`find -iname '*pythran*'` returns nothing; python3-beniget, its own hard
# dependency, is absent too). As written that line fails at parse with
# "Nothing PROVIDES python3-pythran-native". Path (A) is taken - see below.
DEPENDS += "python3-cython-native python3-pybind11-native symoneural-numpy-native symoneural-numpy python3 libgfortran"

# pythran is absent from OE-Core AND from meta-openembedded, and its chain
# (beniget, ply) is absent too. Authoring it in-stack would make the ply
# vendoring collision live. scipy exposes use-pythran as a meson option, so it
# is disabled: the cost is slower fallbacks for Pythran-accelerated kernels,
# not loss of function. BUILD-DESIGN decision, recorded.
EXTRA_OEMESON += "-Duse-pythran=false"

# pyproject-build validates [build-system] requires against the native env even
# with --no-isolation. pythran is unobtainable (absent from OE-Core and
# meta-openembedded, chain missing) and is genuinely unused because
# -Duse-pythran=false. Skipping the check is honest here: the dependency is
# declared but not exercised. numpy IS exercised and is supplied above.
PEP517_BUILD_OPTS += "--skip-dependency-check"

# P1 - pythran is DISABLED, and this is a supported scipy configuration rather
# than a patch, so the pristine guarantee holds and the gast/beniget/ply chain
# never goes live. Verified absent from every layer:
#   find ~/symoneural-bootstrap-master -iname '*pythran*'   ->  nothing
#   python3-beniget ABSENT (pythran's own hard dep); gast and ply PRESENT
# What it costs: SPEED in a few transpiled kernels. NOT CORRECTNESS - scipy
# treats pythran as optional and falls back to compiled C/Fortran paths.
# pythran stays in pending-acquisitions as DEFERRED, not deleted: it gets
# acquired the day a RavenCalc benchmark says the speed matters.
# (the flag itself is set once, above)

# numpy ships its pkg-config file INSIDE the package, not in ${libdir}/pkgconfig:
#   .../site-packages/numpy/_core/lib/pkgconfig/numpy.pc
# OE only puts ${libdir}/pkgconfig and ${datadir}/pkgconfig on PKG_CONFIG_PATH, so
# scipy/meson.build:34 `dependency('numpy')` fails with
#   ERROR: Dependency "numpy" not found (tried pkg-config and config-tool)
# even though the header tree IS staged. Point pkg-config at where numpy actually
# put it. STAGING_DIR_HOST prefix is required - PKG_CONFIG_PATH entries in OE are
# absolute paths into the sysroot, not target paths.
PKG_CONFIG_PATH:prepend = "${STAGING_DIR_HOST}${PYTHON_SITEPACKAGES_DIR}/numpy/_core/lib/pkgconfig:"

# f2py's shebang is `#!/usr/bin/env nativepython3`, which resolves only if
# STAGING_BINDIR_NATIVE is on PATH. scipy/meson.build:207 calls
# `run_command([f2py, '-v'], check: true)`, and meson runs that with a SANITISED
# environment - reproducible with `env -i /path/to/f2py -v`, which gives the same
# "env: 'nativepython3': No such file or directory". The same binary succeeds and
# prints 2.5.3 when PATH carries the native bindir, so the fault is the env-based
# shebang, not f2py.
#
# Rewrite it to an absolute interpreter in THIS recipe's own recipe-sysroot-native,
# which is per-recipe and disposable - no shared state and no acquired source is
# touched. R1 is unaffected: nothing here writes into src/*/source.
do_configure:prepend() {
    f2py="${STAGING_BINDIR_NATIVE}/f2py"
    if [ -f "$f2py" ] && head -1 "$f2py" | grep -q '^#!/usr/bin/env nativepython3'; then
        sed -i "1s|.*|#!${STAGING_BINDIR_NATIVE}/nativepython3|" "$f2py"
        bbnote "f2py shebang pinned to ${STAGING_BINDIR_NATIVE}/nativepython3"
    fi
}

# --- EMPTY PYTHONPATH ENTRY == CURRENT DIRECTORY -----------------------------
# The f2py shebang fix above was necessary but NOT sufficient. With the shebang
# pinned, meson.build:207 still died - and the real cause was hiding two frames
# deeper than the reported error:
#
#   numpy/f2py/__init__.py:13   import subprocess
#     subprocess.py:49            import signal          <- the STDLIB module
#       pristine/scipy/signal/__init__.py:307            <- SCIPY's signal wins
#         from scipy._lib._array_api import ...
#   ModuleNotFoundError: No module named 'scipy'
#
# scipy's own `signal` subpackage SHADOWS the stdlib `signal` that `subprocess`
# imports. It can only do that if scipy's source root is on sys.path, and it is,
# because python3targetconfig.bbclass:17 writes
#     export PYTHONPATH=${STAGING_LIBDIR}/python-sysconfigdata:$PYTHONPATH
# With PYTHONPATH previously unset that expands with a TRAILING COLON, and an
# empty PYTHONPATH entry means THE CURRENT DIRECTORY. meson runs the f2py check
# with cwd = ${S}/scipy, which contains signal/. Hence the collision.
#
# Proven by bisection at the exact failing cwd, same binary all three times:
#   PYTHONPATH=".../python-sysconfigdata:"                  -> ModuleNotFoundError
#   PYTHONPATH=".../python-sysconfigdata"   (no colon)      -> 2.5.3
#   PYTHONSAFEPATH=1 with the trailing colon                -> ModuleNotFoundError
# The third line matters: PYTHONSAFEPATH does NOT strip empty PYTHONPATH
# entries - it only governs sys.path[0]. It is not a fix for this.
#
# So: collapse and trim empty entries. Done in BOTH tasks because ninja can
# re-run meson regeneration during do_compile, which re-runs the f2py check.
# This is generic OE behaviour, not a scipy bug - scipy is just the package
# whose source layout makes an upstream wart fatal.
# Order-independent guard. The class line lives INSIDE a function body, so whether
# our prepend runs before or after it is not something to assume. Seeding PYTHONPATH
# at recipe level means the class's ":$PYTHONPATH" appends to a NON-EMPTY value in
# every ordering - worst case a harmless duplicate, never an empty entry.
export PYTHONPATH = "${STAGING_LIBDIR}/python-sysconfigdata"

symon_fix_pythonpath() {
    PYTHONPATH="$(echo "$PYTHONPATH" | sed -e 's/::*/:/g' -e 's/^://' -e 's/:$//')"
    export PYTHONPATH
    bbnote "PYTHONPATH normalised (no empty entry): ${PYTHONPATH}"
}
do_configure:prepend() {
    symon_fix_pythonpath
}
do_compile:prepend() {
    symon_fix_pythonpath
}
