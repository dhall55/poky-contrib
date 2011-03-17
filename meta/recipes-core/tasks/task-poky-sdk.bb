#
# Copyright (C) 2007 OpenedHand Ltd.
#

DESCRIPTION = "Software Development Tasks for OpenedHand Poky"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${POKYBASE}/LICENSE;md5=3f40d7994397109285ec7b81fdeb3b58 \
                    file://${POKYBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"
DEPENDS = "task-poky"
PR = "r8"

ALLOW_EMPTY = "1"

inherit package_sdk
PACKAGEFUNCS =+ '${@sdk_gen_pkgs(bb.data.getVar('PACKAGES_SDK_GEN',d,1),d)}'

PACKAGES = "\
    task-poky-sdk \
    task-poky-sdk-dbg \
    task-poky-sdk-dev"

RDEPENDS_task-poky-sdk = "\
    autoconf \
    automake \
    binutils \
    binutils-symlinks \
    coreutils \
    cpp \
    cpp-symlinks \
    diffutils \
    gcc \
    gcc-symlinks \
    g++ \
    g++-symlinks \
    gettext \
    make \
    intltool \
    libstdc++ \
    libstdc++-dev \
    libtool \
    perl-module-re \
    perl-module-text-wrap \
    pkgconfig \
    findutils \
    quilt \
    less \
    distcc \
    ldd \
    file \
    tcl"
