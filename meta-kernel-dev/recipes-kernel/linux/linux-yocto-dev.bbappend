FILESEXTRAPATHS := "${THISDIR}/${PN}"

COMPATIBLE_MACHINE = ${MACHINE}

# KMACHINE is the branch to build
# KMACHINE_<MACHINE> = "yocto/${LINUX_KERNEL_TYPE}/${KMACHINE}"
# KMACHINE_qemux86 = "yocto/${LINUX_KERNEL_TYPE}/${KMACHINE}"

# KERNEL_FEATURES are features to be added to the kernel, and must
# point to configurations stored on the 'meta' branch of the kernel
# that is being built.
# KERNEL_FEATURES ?= <FOO>

# Note: put this in your local.conf to avoid multi-kernel build errors
# PREFERRED_PROVIDER_virtual/kernel ?= "linux-yocto-dev"

# It is often nice to have a local clone of the kernel repos, to
# allow patches to be staged, branches created, etc. Modify
# KSRC_linux_yocto_dev to point to your local clone as appropriate.
# KSRC_linux_yocto_dev ?= /path/to/your/local/clone/linux-yocto-2.6.<ver>.git
SRC_URI = "git://${KSRC_linux_yocto_dev};protocol=file;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

KERNEL_REVISION_CHECKING=
SRCREV=${AUTOREV}
#BB_LOCALCOUNT_OVERRIDE = "1"
LOCALCOUNT = "0"
