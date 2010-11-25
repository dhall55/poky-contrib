inherit kernel
require linux-yocto.inc

KMACHINE_qemux86  = "common_pc/base"
KMACHINE_qemux86-64  = "common_pc_64"
KMACHINE_qemuppc  = "qemu_ppc32"
KMACHINE_qemumips = "mti_malta32_be"
KMACHINE_qemuarm  = "arm_versatile_926ejs"
KMACHINE_atom-pc  = "atom-pc"
KMACHINE_routerstationpro = "routerstationpro"
KMACHINE_mpc8315e-rdb = "fsl-mpc8315e-rdb"
KMACHINE_beagleboard = "beagleboard"

# Holding area for board REVs until the full switch to this
# recipe is complete
SRCREV_machine_pn-linux-yocto_qemuarm = "87e00a2d47ba80b4ad1f9170cb3f6cf81f21d739"
SRCREV_machine_pn-linux-yocto_qemumips = "7231e473dd981a28e3cea9f677ed60583e731550"
SRCREV_machine_pn-linux-yocto_qemuppc = "3ab3559637130b65d8889fa74286fdb57935726f"
SRCREV_machine_pn-linux-yocto_qemux86 = "87aacc373557f8849dde8618fbe1f7f8f2af6038"
SRCREV_machine_pn-linux-yocto_qemux86-64 = "87aacc373557f8849dde8618fbe1f7f8f2af6038"
SRCREV_machine_pn-linux-yocto_emenlow = "87aacc373557f8849dde8618fbe1f7f8f2af6038"
SRCREV_machine_pn-linux-yocto_atom-pc = "87aacc373557f8849dde8618fbe1f7f8f2af6038"
SRCREV_machine_pn-linux-yocto_routerstationpro = "773d3a1c8eba563ffcdbf61057ef6e39cee0c88b"
SRCREV_machine_pn-linux-yocto_mpc8315e-rdb = "5ff609967ffe87c49d534d7861a7e0b150517726"
SRCREV_machine_pn-linux-yocto_beagleboard = "87aacc373557f8849dde8618fbe1f7f8f2af6038"
SRCREV_meta_pn-linux-yocto = "ee0a10ab687b29c4d22d47e5b28bc8b3ebb7a8d9"

LINUX_VERSION ?= "2.6.37"
LINUX_VERSION_EXTENSION ?= "-yocto-${LINUX_KERNEL_TYPE}"
PR = "r14"
PV = "${LINUX_VERSION}+git${SRCPV}"
SRCREV_FORMAT = "meta_machine"

# this performs a fixup on the SRCREV for new/undefined BSPs
python __anonymous () {
    import bb, re

    rev = bb.data.getVar("SRCREV_machine", d, 1)
    if rev == "standard":
        bb.data.setVar("SRCREV_machine", "${SRCREV_meta}", d)
}

SRC_URI = "git://git.pokylinux.org/linux-yocto-2.6.37;protocol=git;fullclone=1;branch=${KBRANCH};name=machine \
           git://git.pokylinux.org/linux-yocto-2.6.37;protocol=git;noclone=1;branch=meta;name=meta"


# Functionality flags
KERNEL_REVISION_CHECKING ?= "t"
KERNEL_FEATURES=features/netfilter

# extra tasks
addtask kernel_link_vmlinux after do_compile before do_install
addtask validate_branches before do_patch after do_kernel_checkout

require linux-tools.inc
