#
# Copyright (C) 2011-2012 Intel Corporation
#

DESCRIPTION = "Tasks for core X11 applications"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=3f40d7994397109285ec7b81fdeb3b58 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"
PR = "r35"

PACKAGES = "\
    task-core-x11-base \
    task-core-x11-base-dbg \
    task-core-x11-base-dev \
    "

PACKAGE_ARCH = "${MACHINE_ARCH}"

XSERVER ?= "xserver-kdrive-fbdev"

ALLOW_EMPTY = "1"

# elsa, xserver-nodm-init
VIRTUAL-RUNTIME_graphical_init_manager ?= "xserver-nodm-init"


RDEPENDS_task-core-x11-base = "\
    dbus \
    pointercal \
    matchbox-wm \
    matchbox-keyboard \
    matchbox-keyboard-applet \
    matchbox-keyboard-im \
    matchbox-panel-2 \
    matchbox-desktop \
    matchbox-session \
    ${XSERVER} \
    x11-common \
    ${VIRTUAL-RUNTIME_graphical_init_manager} \
    liberation-fonts \
    xauth \
    xhost \
    xset \
    xrandr"
