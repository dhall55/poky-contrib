inherit kernel

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=d7810fab7487fb0aad327b76f1be7cd7"

FILESDIR = "${@os.path.dirname(bb.data.getVar('FILE',d,1))}/linux-linaro-2.6.35/${MACHINE}"

DESCRIPTION = "Linaro 2.6.35 kernel for ARM7 processors"
KERNEL_IMAGETYPE = "uImage"

SRC_URI = "git://git.linaro.org/kernel/linux-linaro-2.6.35.git;protocol=git \
           file://defconfig \
	   file://0001-OMAP4-enable-smc-instruction-in-new-assembler-versio.patch \
	   file://0001-omap3-beaglexm-fix-EHCI-power-up-GPIO-dir.patch \
	   "

#SRCREV = "${AUTOREV}"
SRCREV = "2207e446f6559ee5c51332c0f64a8a06f48f4d5f"

PV = "2.6.35"
# FIXME: using the following PV breaks the build
#PV = "${PR}+git${SRCREV}"
PR = "r4"

COMPATIBLE_MACHINE = "beagleboard"

S = "${WORKDIR}/git"
