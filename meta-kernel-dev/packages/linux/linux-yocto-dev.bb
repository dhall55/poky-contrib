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

SRC_URI = "git://git.kernel.org/pub/scm/linux/kernel/git/ashfield/linux-yocto-dev.git;protocol=git;nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

SRCREV=${AUTOREV}
SRCREV_machine_pn-linux-yocto-dev ?= "a19d632e7fb478180dbe61720fdde8b25189792c"
SRCREV_meta_pn-linux-yocto-dev ?= "a19d632e7fb478180dbe61720fdde8b25189792c"

LINUX_VERSION ?= "2.6.39"
LINUX_VERSION_EXTENSION ?= "-yoctodev-${LINUX_KERNEL_TYPE}"
PR = "r0"
PV = "${LINUX_VERSION}+git"
SRCREV_FORMAT = "meta_machine"

COMPATIBLE_MACHINE = "(qemuarm|qemux86|qemuppc|qemumips|qemux86-64|mpc8315e-rdb|routerstationpro|beagleboard)"

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
