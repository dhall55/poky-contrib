FILESEXTRAPATHS := "${THISDIR}/${PN}"

COMPATIBLE_MACHINE = ${MACHINE}

# It is often nice to have a local clone of the kernel repos, to
# allow patches to be staged, branches created, etc. Modify
# KSRC to point to your local clone as appropriate.
# KSRC ?= /path/to/your/bare/clone/yocto-kernell

# KMACHINE is the branch to be built, or alternatively
# KBRANCH can be directly set.

# KBRANCH ?= "${KMACHINE}-${LINUX_KERNEL_TYPE}"
KSRC ?= /home/bruce/poky-kernel/default_kernel-stable
KBRANCH ?= "${KMACHINE}-${LINUX_KERNEL_TYPE}"

SRC_URI = "git://${KSRC};nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

KERNEL_REVISION_CHECKING=
SRCREV=${AUTOREV}
# BB_LOCALCOUNT_OVERRIDE = "1"
LOCALCOUNT = "0"

