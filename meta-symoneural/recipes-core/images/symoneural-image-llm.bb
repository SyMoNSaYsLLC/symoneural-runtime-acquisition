# Clean-target proof image for the LLM runtime: a rootfs assembled by opkg from the
# package feed containing packagegroup-symoneural-llm and its RDEPENDS. No source
# tree, no devtool workspace, no pip, no build frontends, NO MODEL WEIGHTS
# (reconstruction v1.1 §37/§68; models are external inputs).
SUMMARY = "SyMoNeuRaL LLM clean-root proof image"
LICENSE = "MIT"

inherit image

IMAGE_INSTALL = "packagegroup-symoneural-llm"
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""
IMAGE_FSTYPES = "tar.gz"
IMAGE_INSTALL:remove = "packagegroup-core-boot"
NO_RECOMMENDATIONS = "1"
# no qemuboot and no kernel: nothing boots this tarball (see symoneural-image-api)
IMAGE_CLASSES:remove = "qemuboot"
KERNEL_DEPLOY_DEPEND = ""
KERNELDEPMODDEPEND = ""
