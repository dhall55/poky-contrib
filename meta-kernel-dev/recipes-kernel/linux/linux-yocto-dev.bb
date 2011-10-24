inherit kernel
require recipes-kernel/linux/linux-yocto.inc

KMACHINE = "yocto/standard/base"
KMACHINE_qemux86  = "yocto/standard/common-pc/base"
KMACHINE_qemux86-64  = "yocto/standard/common-pc-64/base"
KMACHINE_qemuppc  = "yocto/standard/qemu-ppc32"
KMACHINE_qemumips = "yocto/standard/mti-malta32-be"
KMACHINE_qemuarm  = "yocto/standard/arm-versatile-926ejs"
KMACHINE_atom-pc  = "yocto/standard/common-pc/atom-pc"
KMACHINE_routerstationpro = "yocto/standard/routerstationpro"
KMACHINE_mpc8315e-rdb = "yocto/standard/fsl-mpc8315e-rdb"
KMACHINE_beagleboard = "yocto/standard/beagleboard"

KBRANCH = ${KMACHINE}
KMETA = meta

SRC_URI = "git://git.pokylinux.org/linux-yocto-dev;protocol=git;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

SRCREV=${AUTOREV}
SRCREV_machine_pn-linux-yocto-dev ?= "8e10cd74342c7f5ce259cceca36f6eba084f5d58"
SRCREV_meta_pn-linux-yocto-dev ?= "3fc7c4c685f4e1d7d5fc7aea08536ca472fa1821"

LINUX_VERSION ?= "3.1"
LINUX_VERSION_EXTENSION ?= "-yoctodev-${LINUX_KERNEL_TYPE}"
PR = "r0"
PV = "${LINUX_VERSION}+git${SRCPV}"
SRCREV_FORMAT = "meta_machine"

COMPATIBLE_MACHINE = "(qemuarm|qemux86|qemuppc|qemumips|qemux86-64|mpc8315e-rdb|routerstationpro)"

# Functionality flags
KERNEL_REVISION_CHECKING=
KERNEL_FEATURES="features/netfilter"
KERNEL_FEATURES_append_qemux86=" cfg/sound"
KERNEL_FEATURES_append_qemux86-64=" cfg/sound"

# extra tasks
addtask kernel_link_vmlinux after do_compile before do_install
addtask validate_branches before do_patch after do_kernel_checkout
addtask kernel_configcheck after do_configure before do_compile

require recipes-kernel/linux/linux-tools.inc
