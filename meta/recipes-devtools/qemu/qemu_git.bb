require qemu.inc

SRCREV = "cf36b31db209a261ee3bc2737e788e1ced0a1bec"

LIC_FILES_CHKSUM = "file://COPYING;md5=441c28d2cf86e15a37fa47e15a72fbac \
                    file://COPYING.LIB;endline=24;md5=c04def7ae38850e7d3ef548588159913"

PV = "1.0+git"
PR = "r0"

FILESPATH = "${FILE_DIRNAME}/qemu-${PV}/:${FILE_DIRNAME}/qemu-git/"
FILESDIR = "${WORKDIR}"

SRC_URI = "\
    git://git.qemu.org/qemu.git;protocol=git \
    file://powerpc_rom.bin \
    "
S = "${WORKDIR}/git"

DEFAULT_PREFERENCE = "-1"
