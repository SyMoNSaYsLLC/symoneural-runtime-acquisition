# Clean-target proof image for the CLI runtime: a rootfs assembled by opkg from the
# package feed containing packagegroup-symoneural-cli and its RDEPENDS. No source
# tree, no devtool workspace, no pip, no build frontends (reconstruction v1.1 §37/§68).
SUMMARY = "SyMoNeuRaL CLI clean-root proof image"
LICENSE = "MIT"

inherit image

IMAGE_INSTALL = "packagegroup-symoneural-cli"
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""
IMAGE_FSTYPES = "tar.gz"
IMAGE_INSTALL:remove = "packagegroup-core-boot"
NO_RECOMMENDATIONS = "1"
# no qemuboot: nothing boots this tarball under qemu (see symoneural-image-api)
IMAGE_CLASSES:remove = "qemuboot"
# no kernel either: image.bbclass hooks do_build on virtual/kernel:do_deploy and
# do_rootfs on virtual/kernel:do_packagedata (depmod data). A userspace proof root
# installs no kernel modules; both hooks are emptied.
KERNEL_DEPLOY_DEPEND = ""
KERNELDEPMODDEPEND = ""
