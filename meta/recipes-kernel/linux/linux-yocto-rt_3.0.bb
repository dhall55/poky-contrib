inherit kernel
require recipes-kernel/linux/linux-yocto.inc

KMACHINE = "yocto/standard/preempt-rt/base"
KMACHINE_qemux86  = "common-pc"
KMACHINE_qemux86-64  = "common-pc-64"

KBRANCH = ${KMACHINE}
KBRANCH_qemux86 = "yocto/standard/preempt-rt/base"
KBRANCH_qemux86-64 = "yocto/standard/preempt-rt/base"
KMETA = meta

LINUX_VERSION ?= "3.0"
LINUX_KERNEL_TYPE = "preempt-rt"
LINUX_VERSION_EXTENSION ?= "-yocto-${LINUX_KERNEL_TYPE}"

SRCREV_machine_qemux86 = ${AUTOREV}
SRCREV_machine_qemux86-64 = ${AUTOREV}
SRCREV_machine_atom-pc = ${AUTOREV}
SRCREV_machine = ${AUTOREV}
SRCREV_meta = ${AUTOREV}

PR = "r0"
PV = "${LINUX_VERSION}+git${SRCPV}"
SRCREV_FORMAT = "meta_machine"

SRC_URI = "git://git.yoctoproject.org/linux-yocto-3.0.git;protocol=git;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

COMPATIBLE_MACHINE = "(qemux86|qemux86-64)"

# Functionality flags
KERNEL_REVISION_CHECKING ?= "t"
KERNEL_FEATURES=features/netfilter
KERNEL_FEATURES_append=" features/taskstats"
KERNEL_FEATURES_append_qemux86=" cfg/sound"
KERNEL_FEATURES_append_qemux86-64=" cfg/sound"

YOCTO_KERNEL_META_DATA=t

# extra tasks
addtask kernel_link_vmlinux after do_compile before do_install
addtask validate_branches before do_patch after do_kernel_checkout
addtask kernel_configcheck after do_configure before do_compile

require recipes-kernel/linux/linux-tools.inc
