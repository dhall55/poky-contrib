SECTION = "libs"
DESCRIPTION = "theora  is a high-quality video codec \
that is free of intellectual property restrictions"
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://COPYING;md5=cf91718f59eb6a83d06dc7bcaf411132"

DEPENDS = "pkgconfig libogg"

INC_PR = "r4"

SRC_URI = "http://downloads.xiph.org/releases/theora/libtheora-${PV}.tar.bz2" 

inherit autotools

EXTRA_OECONF = "--disable-examples"

LEAD_SONAME = "libtheora.so.0"

