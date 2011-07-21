FILESEXTRAPATHS := "${THISDIR}/${PN}"

COMPATIBLE_MACHINE = ${MACHINE}

# KMACHINE is the branch to build
# KMACHINE_<MACHINE> ?= "yocto/${LINUX_KERNEL_TYPE}/${KMACHINE}"

# KERNEL_FEATURES are features to be added to the kernel, and must
# point to configurations stored on the 'meta' branch of the kernel
# that is being built.
# KERNEL_FEATURES ?= <FOO>

# It is often nice to have a local clone of the kernel repos, to
# allow patches to be staged, branches created, etc. Modify

# KSRC_linux_yocto to point to your local clone as appropriate.
# KSRC_linux_yocto ?= /path/to/local/linux-yocto-3.0
KMACHINE ?= "yocto/${LINUX_KERNEL_TYPE}/${KMACHINE}"

SRC_URI = "git://${KSRC_linux_yocto};protocol=file;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

KERNEL_REVISION_CHECKING=
SRCREV=${AUTOREV}
#BB_LOCALCOUNT_OVERRIDE = "1"
LOCALCOUNT = "0"
