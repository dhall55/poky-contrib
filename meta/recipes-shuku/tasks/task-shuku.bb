#
# Copyright (C) 2012 Intel Corporation
#

DESCRIPTION = "Shuku image tasks"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=3f40d7994397109285ec7b81fdeb3b58 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"
PR = "r1"

PACKAGES = "\
    task-core-x11-base \
    task-core-x11-base-dbg \
    task-core-x11-base-dev \
    "

PACKAGE_ARCH = "${MACHINE_ARCH}"
ALLOW_EMPTY = "1"

XSERVER ?= "xserver-kdrive-fbdev"
VIRTUAL-RUNTIME_graphical_init_manager ?= "xserver-nodm-init"

RDEPENDS_task-shuku = "\
    ${XSERVER} \
    x11-common \
    ${VIRTUAL-RUNTIME_graphical_init_manager} \
    matchbox-wm \
    matchbox-panel-2 \
    matchbox-desktop \
    matchbox-session \
    liberation-fonts \
    xauth \
    xhost \
    xset \
    xrandr"

# keyboard, pointercal, split out X into core task
