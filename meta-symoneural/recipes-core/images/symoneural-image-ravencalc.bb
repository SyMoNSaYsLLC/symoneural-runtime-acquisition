# Clean-target proof image for RavenCalc: opkg-assembled root with
# packagegroup-symoneural-ravencalc only. tools/ravencalc-clean-root-proof runs the
# target interpreter's imports and one integral/matrix solve through compute.py.
SUMMARY = "SyMoNeuRaL RavenCalc clean-root proof image"
LICENSE = "MIT"
inherit image
IMAGE_INSTALL = "packagegroup-symoneural-ravencalc"
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""
IMAGE_FSTYPES = "tar.gz"
IMAGE_INSTALL:remove = "packagegroup-core-boot"
NO_RECOMMENDATIONS = "1"
# qemux86-64's machine conf adds qemuboot, which drags qemu-system-native,
# qemu-helper-native and (through virglrenderer) mesa-tools-native into a build
# whose only product is a rootfs tarball. The first image build spent tasks
# 5300-5682 of 5735 there and died mid mesa-tools-native. Nothing boots this
# tarball under qemu; tools/*-clean-root-proof runs the target interpreter
# through its own ld.so.
IMAGE_CLASSES:remove = "qemuboot"
