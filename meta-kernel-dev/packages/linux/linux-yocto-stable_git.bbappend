FILESEXTRAPATHS := "${THISDIR}/${PN}"

COMPATIBLE_MACHINE = ${MACHINE}

# It is often nice to have a local clone of the kernel repos, to
# allow patches to be staged, branches created, etc. Modify
# KSRC to point to your local clone as appropriate.
# KSRC ?= /path/to/your/bare/clone/yocto-kernell
KBRANCH ?= "${KMACHINE}-${LINUX_KERNEL_TYPE}"

SRC_URI = "git://${KSRC};fullclone=1;branch=${KBRANCH};name=machine \
           git://${KSRC};noclone=1;branch=wrs_meta;name=meta"

KERNEL_REVISION_CHECKING=
KERNEL_BRANCH_CHECKING=
SRCREV=${AUTOREV}
BB_LOCALCOUNT_OVERRIDE = "1"
LOCALCOUNT = "0"

