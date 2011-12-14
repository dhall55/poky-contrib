inherit kernel
require recipes-kernel/linux/linux-yocto.inc

#KMACHINE = "yocto/standard/tiny/base"
KMACHINE = "yocto/standard/base"

KBRANCH = ${KMACHINE}

LINUX_VERSION ?= "3.0.12"

#SRCREV_machine ?= "f389d310965a56091f688b28ea8be6d9cbb7fbbe"
#SRCREV_meta ?= "caa74f86f42f6ecc22c3e9f380176b2695579e18"
SRCREV_machine ?= ${AUTOREV}
SRCREV_meta ?= ${AUTOREV}

PR = "r0"
PV = "${LINUX_VERSION}+git${SRCPV}"

SRC_URI = "git://git.yoctoproject.org/linux-yocto-3.0;protocol=git;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

#COMPATIBLE_MACHINE = "(qemuarm|qemux86|qemuppc|qemumips|qemux86-64)"
COMPATIBLE_MACHINE = "(qemux86|qemux86-64)"

# Functionality flags
KERNEL_FEATURES=""
