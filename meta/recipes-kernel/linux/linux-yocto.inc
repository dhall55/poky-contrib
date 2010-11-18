DESCRIPTION = "Yocto Kernel"
SECTION = "kernel"
LICENSE = "GPL"

# map the poky machine to a 'kernel machine'
KMACHINE = "UNDEFINED"
KMACHINE_qemux86  = "common_pc"
KMACHINE_qemux86-64  = "common_pc_64"
KMACHINE_qemuppc  = "qemu_ppc32"
KMACHINE_qemumips = "mti_malta32_be"
KMACHINE_qemuarm  = "arm_versatile_926ejs"
KMACHINE_atom-pc  = "atom-pc"
KMACHINE_routerstationpro = "routerstationpro"
KMACHINE_mpc8315e-rdb = "fsl-mpc8315e-rdb"
KMACHINE_beagleboard = "beagleboard"

COMPATIBLE_MACHINE = "(qemuarm|qemux86|qemuppc|qemumips|qemux86-64|atom-pc|routerstationpro|mpc8315e-rdb|beagleboard)"

LINUX_KERNEL_TYPE ?= standard

do_patch[depends] = "kern-tools-native:do_populate_sysroot"

addtask kernel_configme before do_configure after do_patch
addtask kernel_configcheck after do_configure before do_compile

# pick up the rest of the shared functions
inherit kernel-yocto

B = "${WORKDIR}/linux-${KMACHINE}-${LINUX_KERNEL_TYPE}-build"
