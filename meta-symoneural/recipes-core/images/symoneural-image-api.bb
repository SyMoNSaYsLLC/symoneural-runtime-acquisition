# Clean-target proof image for the API runtime (reconstruction v1.1 §37/§42):
# a root filesystem assembled by opkg FROM THE PACKAGE FEED containing only
# packagegroup-symoneural-api and what its RDEPENDS pull in. No source tree, no
# devtool workspace, no pip, no build frontends. tools/api-clean-root-proof
# extracts the tarball and runs the target interpreter's imports against it.
SUMMARY = "SyMoNeuRaL API clean-root proof image"
LICENSE = "MIT"

inherit image

IMAGE_INSTALL = "packagegroup-symoneural-api"
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""
IMAGE_FSTYPES = "tar.gz"
# no kernel, no bootloader: this is a userspace root for import/service proofs
IMAGE_INSTALL:remove = "packagegroup-core-boot"
NO_RECOMMENDATIONS = "1"
