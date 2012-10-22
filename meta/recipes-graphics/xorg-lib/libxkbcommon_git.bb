SUMMARY = "Generic XKB keymap library"

DESCRIPTION = "libxkbcommon is a keymap compiler and support library which \
processes a reduced subset of keymaps as defined by the XKB specification."

LICENSE = "MIT & MIT-style"

require xorg-lib-common.inc

DEPENDS = "flex-native bison-native"

LIC_FILES_CHKSUM = "file://COPYING;md5=9c0b824e72a22f9d2c40b9c93b1f0ddc"

SRCREV = "1c880887666f84e08ea1752bb8a5ab2a7bf1d8a0"
PV = "0.1.0+git${SRCPV}"
PR = "r0"

SRC_URI = "git://anongit.freedesktop.org/xorg/lib/libxkbcommon;protocol=git"
S = "${WORKDIR}/git"
