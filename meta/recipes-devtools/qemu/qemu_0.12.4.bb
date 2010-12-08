require qemu.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=441c28d2cf86e15a37fa47e15a72fbac \
                    file://COPYING.LIB;endline=24;md5=c04def7ae38850e7d3ef548588159913"

PR = "r23"

FILESPATH = "${FILE_DIRNAME}/qemu-${PV}"
FILESDIR = "${WORKDIR}"

SRC_URI = "\
    http://download.savannah.gnu.org/releases/qemu/qemu-${PV}.tar.gz \
    file://workaround_bad_futex_headers.patch \
    file://qemu-git-qemugl-host.patch \
    file://no-strip.patch \
    file://fix-dirent.patch \
    file://fix-nogl.patch \
    file://qemugl-allow-glxcontext-release.patch \
    file://linker-flags.patch \
    file://init-info.patch \
    file://qemu-vmware-vga-depth.patch \
    file://qemu-ppc-hack.patch \
    file://enable-i386-linux-user.patch \
    file://arm-cp15-fix.patch \
    file://cursor-shadow-fix.patch \
    file://vmware-vga-fifo-rewind.patch \
    file://fix-configure-checks.patch \
    file://powerpc_rom.bin \
    file://arm_timer-fix-oneshot-mode.patch \
    file://arm_timer-reload-timer-when-enabled.patch"

do_install_append () {
        install -d ${D}${datadir}/qemu
        install -m 0755 ${WORKDIR}/powerpc_rom.bin ${D}${datadir}/qemu
}

S = "${WORKDIR}/qemu-${PV}"
