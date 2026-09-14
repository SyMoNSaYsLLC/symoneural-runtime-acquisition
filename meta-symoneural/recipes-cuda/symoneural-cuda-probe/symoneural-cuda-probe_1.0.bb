# The C5 proof for the estate CUDA authority: a first-party sm_120 kernel cross-built
# through symoneural-cuda (native nvcc, target headers/libs, cross g++ host compiler),
# packaged, and run on the target root against the host driver's libcuda.so.1.
SUMMARY = "SyMoNeuRaL CUDA authority probe - sm_120 kernel built and run through the estate toolkit"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://probe.cu file://CMakeLists.txt"
S = "${UNPACKDIR}"

inherit cmake symoneural-cuda
