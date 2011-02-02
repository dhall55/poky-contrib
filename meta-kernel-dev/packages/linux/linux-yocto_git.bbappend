FILESEXTRAPATHS := "${THISDIR}/${PN}"

COMPATIBLE_MACHINE = ${MACHINE}

# It is often nice to have a local clone of the kernel repos, to
# allow patches to be staged, branches created, etc. Modify

# KSRC to point to your local clone as appropriate.
# KSRC ?= /path/to/your/bare/clone/yocto-kernel

# KMACHINE is the branch to build
# KMACHINE_<MACHINE> ?= "yocto/${LINUX_KERNEL_TYPE}/${KMACHINE}"

# KERNEL_FEATURES are features to be added to the kernel, and must
# point to configurations stored on the 'meta' branch of the kernel
# that is being built.
# KERNEL_FEATURES ?= <FOO>

SRC_URI = "git://${KSRC};protocol=git;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

KERNEL_REVISION_CHECKING=
SRCREV=${AUTOREV}
#BB_LOCALCOUNT_OVERRIDE = "1"
LOCALCOUNT = "0"
