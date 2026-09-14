# libsymoneural-api + symoneural-api-util: the NATIVE half of the SyMoNeuRaL API
# (reconstruction v1.1 §29-§34). C17, libc/POSIX only - readelf NEEDED must show
# libc.so.6 and nothing else; tools/api-clean-root-proof checks that on the target
# package. ABI v1.0.0 = (MAJOR<<16)|(MINOR<<8)|PATCH, SONAME libsymoneural-api.so.1.
#
# First-party source, built from the committed tree HEAD:Symoneural-API/app by
# symoneural-firstparty. LICENSE is CLOSED: SyMoNeuRaL's own code carries no
# licence text in the repository today; that declaration is Garrett's to make.
SUMMARY = "SyMoNeuRaL API native library and utility"
HOMEPAGE = "https://symoneural.com"
LICENSE = "CLOSED"

inherit symoneural-firstparty cmake
SYMON_FP_PATH = "Symoneural-API/app"

# -Werror is upstream's (ours); cross builds get the same treatment as the host run
EXTRA_OECMAKE += "-DCMAKE_BUILD_TYPE=RelWithDebInfo"

do_install:append() {
    install -d ${D}${datadir}/symoneural-api
    install -m 0644 ${S}/SOURCE-TREE ${D}${datadir}/symoneural-api/SOURCE-TREE
}

# debian.bbclass would rename ${PN} to libsymoneural-api1 because it holds only a
# shared library; an allarch packagegroup cannot depend on a dynamically renamed
# package (do_package_write_ipk ERROR). Names are fixed here, and the library's
# identity is its SONAME, not the package name.
DEBIAN_NOAUTONAME:${PN} = "1"
DEBIAN_NOAUTONAME:${PN}-util = "1"
DEBIAN_NOAUTONAME:${PN}-dev = "1"
DEBIAN_NOAUTONAME:${PN}-dbg = "1"
DEBIAN_NOAUTONAME:${PN}-staticdev = "1"
DEBIAN_NOAUTONAME:${PN}-src = "1"
PACKAGES =+ "${PN}-util"
FILES:${PN} = "${libdir}/libsymoneural-api.so.* ${datadir}/symoneural-api/SOURCE-TREE"
FILES:${PN}-util = "${bindir}/symoneural-api-util"
FILES:${PN}-dev += "${includedir}/symoneural ${libdir}/libsymoneural-api.so"
FILES:${PN}-staticdev = "${libdir}/libsymoneural-api.a"
RDEPENDS:${PN}-util += "${PN}"
