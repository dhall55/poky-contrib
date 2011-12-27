DESCRIPTION = "Library for Freeware Advanced Audio Coder (MPEG-2/MPEG-4 AAC) audio compression format."
SECTION = "libs"
PRIORITY = "optional"
DEPENDS = ""
LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=3bf50002aefd002f49e7bb854063f7e7 \
                    file://libfaac/coder.h;beginline=5;endline=17;md5=fa1fd6a5fa8cdc877d63a12530d273e0"

PR = "r0"

inherit autotools

SRC_URI = "${SOURCEFORGE_MIRROR}/faac/${PN}-${PV}.tar.gz"
S = "${WORKDIR}/${PN}"

PACKAGES =+ "lib${PN} lib${PN}-dev"

FILES_${PN} = " ${bindir}/faac "
FILES_lib${PN} = " ${libdir}/libfaac.so.*"
FILES_lib${PN}-dev = " ${includedir}/faac.h ${includedir}/faaccfg.h ${libdir}/libfaac.so ${libdir}/libfaac.la ${libdir}/libfaac.a "

SRC_URI[md5sum] = "80763728d392c7d789cde25614c878f6"
SRC_URI[sha256sum] = "c5141199f4cfb17d749c36ba8cfe4b25f838da67c22f0fec40228b6b9c3d19df"
