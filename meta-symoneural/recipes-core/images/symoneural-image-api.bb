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
# qemux86-64's machine conf adds qemuboot, which drags qemu-system-native,
# qemu-helper-native and (through virglrenderer) mesa-tools-native into a build
# whose only product is a rootfs tarball. The first image build spent tasks
# 5300-5682 of 5735 there and died mid mesa-tools-native. Nothing boots this
# tarball under qemu; tools/*-clean-root-proof runs the target interpreter
# through its own ld.so.
IMAGE_CLASSES:remove = "qemuboot"
