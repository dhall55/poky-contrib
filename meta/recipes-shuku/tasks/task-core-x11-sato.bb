#
# Copyright (C) 2012 Intel Corp
#

DESCRIPTION = "Shuku Tasks for Poky"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=3f40d7994397109285ec7b81fdeb3b58 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"
PR = "r0"

PACKAGES = "\
    task-shuku \
    task-shuku-dbg \
    task-shuku-dev \
    "

PACKAGE_ARCH = "${MACHINE_ARCH}"

ALLOW_EMPTY = "1"

NETWORK_MANAGER ?= "connman-gnome"
NETWORK_MANAGER_libc-uclibc = ""

RDEPENDS_task-core-x11-sato = "\
    matchbox-panel \
    matchbox-desktop \
    matchbox-session-sato \
    matchbox-keyboard \
    matchbox-stroke \
    xcursor-transparent-theme \
    sato-icon-theme \
    settings-daemon \
    gtk-sato-engine \
    x11vnc \
    ${NETWORK_MANAGER}"
