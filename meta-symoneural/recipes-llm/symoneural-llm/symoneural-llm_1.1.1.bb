# libsymoneural-llm - the SyMoNeuRaL-owned inference ABI over libllama + libggml
# (reconstruction v1.1 §49-§56, L3), plus symoneural-llm-util. First-party code built
# from the committed tree HEAD:Symoneural-LLM/app (symoneural-firstparty); the native
# dependencies are the estate's own packages, linked through llama.pc from the
# sysroot - never a host library, never a build tree.
SUMMARY = "SyMoNeuRaL LLM native library (libsymoneural-llm) and utility"
HOMEPAGE = "https://symoneural.com"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=f6737acf372c75a15aaeb6e6eca2c340"

inherit symoneural-firstparty cmake pkgconfig
SYMON_FP_PATH = "Symoneural-LLM/app"

DEPENDS += "symoneural-llama-cpp symoneural-ggml"
EXTRA_OECMAKE += "-DCMAKE_BUILD_TYPE=RelWithDebInfo"

do_install:append() {
    install -d ${D}${datadir}/symoneural-llm
    install -m 0644 ${S}/SOURCE-TREE ${D}${datadir}/symoneural-llm/SOURCE-TREE
}

# debian.bbclass would rename ${PN} to libsymoneural-llm1 because it holds only a
# shared library; the allarch packagegroup cannot depend on a dynamically renamed
# package, and tools/check-native-linkage.py addresses the package as
# symoneural-llm. Names are fixed here; the library's identity is its SONAME.
DEBIAN_NOAUTONAME:${PN} = "1"
DEBIAN_NOAUTONAME:${PN}-util = "1"
DEBIAN_NOAUTONAME:${PN}-dev = "1"
DEBIAN_NOAUTONAME:${PN}-dbg = "1"
DEBIAN_NOAUTONAME:${PN}-staticdev = "1"
DEBIAN_NOAUTONAME:${PN}-src = "1"

PACKAGES =+ "${PN}-util"
FILES:${PN} = "${libdir}/libsymoneural-llm.so.* ${datadir}/symoneural-llm/SOURCE-TREE"
FILES:${PN}-util = "${bindir}/symoneural-llm-util"
FILES:${PN}-dev += "${includedir}/symoneural ${libdir}/libsymoneural-llm.so"
FILES:${PN}-staticdev = "${libdir}/libsymoneural-llm.a"
RDEPENDS:${PN}-util += "${PN}"
