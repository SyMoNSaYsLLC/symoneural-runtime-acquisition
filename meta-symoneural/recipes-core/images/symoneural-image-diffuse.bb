# Clean-target proof image for the Diffuse runtime: a rootfs assembled by opkg from the
# package feed containing packagegroup-symoneural-diffuse and its RDEPENDS. No source
# tree, no devtool workspace, no pip, no build frontends, NO MODEL WEIGHTS
# (reconstruction v1.1 section 37/68; models are external inputs).
SUMMARY = "SyMoNeuRaL Diffuse clean-root proof image"
LICENSE = "MIT"

inherit image

# python3-modules is here for the HARNESS, not for the runtime.
#
# tools/clean-root-proof is shared by every runtime and its proof bodies are Python; it
# looks for ${R}/usr/bin/python3.1[0-9] and refuses a root without one. Diffuse's actual
# surface is pure C++ - packagegroup-symoneural-diffuse is one package - so the
# interpreter is scaffolding. tools/proofs/diffuse.py imports ONLY the standard library
# and drives sd-cli as a subprocess; it never imports anything from the Diffuse runtime,
# because there is nothing importable to import. Reading the manifest, the Diffuse
# surface is the symoneural-* rows; everything python3-* is the harness.
IMAGE_INSTALL = "packagegroup-symoneural-diffuse python3-modules"
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""
IMAGE_FSTYPES = "tar.gz"
IMAGE_INSTALL:remove = "packagegroup-core-boot"
NO_RECOMMENDATIONS = "1"
# no qemuboot and no kernel: nothing boots this tarball (see symoneural-image-api)
IMAGE_CLASSES:remove = "qemuboot"
KERNEL_DEPLOY_DEPEND = ""
KERNELDEPMODDEPEND = ""
