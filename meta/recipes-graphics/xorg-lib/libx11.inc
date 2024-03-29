SUMMARY = "Xlib: C Language X Interface library"

DESCRIPTION = "This package provides a client interface to the X Window \
System, otherwise known as 'Xlib'.  It provides a complete API for the \
basic functions of the window system."

require xorg-lib-common.inc

inherit siteinfo

FILESPATH = "${FILE_DIRNAME}/libx11"

PE = "1"
INC_PR = "r10"

PROVIDES = "virtual/libx11"

XORG_PN = "libX11"
LICENSE = "MIT & MIT-style & BSD"
LIC_FILES_CHKSUM = "file://COPYING;md5=172255dee66bb0151435b2d5d709fcf7"

DEPENDS += "xproto xextproto xtrans libxcb kbproto inputproto"
DEPENDS += "xproto-native"

EXTRA_OECONF += "--with-keysymdefdir=${STAGING_INCDIR}/X11/ --disable-xf86bigfont"
EXTRA_OEMAKE += 'CWARNFLAGS=""'

# Let people with incredibly archaic requirements enable Xcms, but disable it by
# default.
PACKAGECONFIG ??= ""
PACKAGECONFIG[xcms] = "--enable-xcms,--disable-xcms"

# src/util/makekeys needs to be compiled natively, so tell it what compiler to
# use.
export CC_FOR_BUILD = "${BUILD_CC}"
export CFLAGS_FOR_BUILD = "${BUILD_CFLAGS} -D_GNU_SOURCE"
export CPPFLAGS_FOR_BUILD = "${BUILD_CPPFLAGS}"
export LDFLAGS_FOR_BUILD = "${BUILD_LDFLAGS}"

PACKAGES =+ "${PN}-xcb"

FILES_${PN} += "${datadir}/X11/XKeysymDB ${datadir}/X11/XErrorDB ${libdir}/X11/Xcms.txt"
FILES_${PN}-xcb += "${libdir}/libX11-xcb.so.*"
FILES_${PN}-locale += "${datadir}/X11/locale ${libdir}/X11/locale"

# Multiple libx11 derivatives from from this file and are selected by virtual/libx11
# A world build should only build the correct version, not all of them.
EXCLUDE_FROM_WORLD = "1"
