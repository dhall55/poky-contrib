inherit kernel
require recipes-kernel/linux/linux-yocto.inc

KMACHINE = "common-pc"
KMACHINE_qemux86  = "common-pc"
KMACHINE_qemux86-64  = "common-pc-64"
KMACHINE_qemuppc  = "qemu-ppc32"
KMACHINE_qemumips = "mti-malta32-be"
KMACHINE_qemuarm  = "arm-versatile-926ejs"
KMACHINE_atom-pc  = "atom-pc"
KMACHINE_routerstationpro = "routerstationpro"
KMACHINE_mpc8315e-rdb = "fsl-mpc8315e-rdb"
KMACHINE_beagleboard = "beagleboard"

KBRANCH = "standard/default/base"
KBRANCH_qemux86  = "standard/default/common-pc/base"
KBRANCH_qemux86-64  = "standard/default/common-pc-64/base"
KBRANCH_qemuppc  = "standard/default/qemu-ppc32"
KBRANCH_qemumips = "standard/default/mti-malta32-be"
KBRANCH_qemuarm  = "standard/default/arm-versatile-926ejs"
KBRANCH_atom-pc  = "yocto/standard/common-pc/atom-pc"
KBRANCH_routerstationpro = "yocto/standard/routerstationpro"
KBRANCH_mpc8315e-rdb = "yocto/standard/fsl-mpc8315e-rdb"
KBRANCH_beagleboard = "yocto/standard/beagleboard"

SRC_URI = "git://git.pokylinux.org/linux-yocto-dev;protocol=git;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

SRCREV=${AUTOREV}

LINUX_VERSION ?= "3.2"
LINUX_VERSION_EXTENSION ?= "-yoctodev-${LINUX_KERNEL_TYPE}"
PR = "r0"

COMPATIBLE_MACHINE = "(qemuarm|qemux86|qemuppc|qemumips|qemux86-64|mpc8315e-rdb|routerstationpro)"

# Functionality flags
KERNEL_REVISION_CHECKING=
KERNEL_FEATURES="features/netfilter"
KERNEL_FEATURES_append_qemux86=" cfg/sound"
KERNEL_FEATURES_append_qemux86-64=" cfg/sound"

require recipes-kernel/linux/linux-tools.inc
