FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

# atom-pc support
COMPATIBLE_MACHINE_atom-pc = "atom-pc"
KMACHINE_atom-pc = "atom-pc"
KBRANCH_atom-pc = "yocto/standard/preempt-rt/base"
#SRCREV_machine_pn-linux-yocto-rt_atom-pc = ${AUTOREV}

# beagleboard support
COMPATIBLE_MACHINE_beagleboard = "beagleboard"
KMACHINE_beagleboard = "beagleboard"
KBRANCH_beagleboard = "yocto/standard/preempt-rt/base"
#SRCREV_machine_pn-linux-yocto-rt_beagleboard = ${AUTOREV}

# mpc8315e-rdb support
COMPATIBLE_MACHINE_mpc8315e-rdb = "mpc8315e-rdb"
KMACHINE_mpc8315e-rdb = "fsl-mpc8315e-rdb"
KBRANCH_mpc8315e-rdb = "yocto/standard/preempt-rt/base"
#SRCREV_machine_pn-linux-yocto-rt_mpc8315e-rdb = ${AUTOREV}

# routerstationpro support
COMPATIBLE_MACHINE_routerstationpro = "routerstationpro"
KMACHINE_routerstationpro = "routerstationpro"
KBRANCH_routerstationpro = "yocto/standard/preempt-rt/base"
#SRCREV_machine_pn-linux-yocto-rt_routerstationpro = ${AUTOREV}

SRCREV_machine = ${AUTOREV}
