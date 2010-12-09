require recipes-kernel/linux/linux.inc

FILESDIR = "${@os.path.dirname(bb.data.getVar('FILE',d,1))}/linux-linaro-2.6.35/${MACHINE}"

DESCRIPTION = "Linaro 2.6.35 kernel for ARM7 processors"
KERNEL_IMAGETYPE = "uImage"

SRC_URI = "git://git.linaro.org/kernel/linux-linaro-2.6.35.git;protocol=git \
           file://defconfig"

SRCREV = "${AUTOREV}"

PV = "2.6.35"
# FIXME: using the following PV breaks the build
#PV = "${PR}+git${SRCREV}"
PR = "r1"

COMPATIBLE_MACHINE = "beagleboard-linaro"

S = "${WORKDIR}/git"
