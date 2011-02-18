DESCRIPTION = "Library that offer a standardized API to control radio oriented equipment through a computer interface."
HOMEPAGE = "http://hamlib.sourceforge.net/"
SRC_URI = "http://sourceforge.net/projects/hamlib/files/hamlib/${PV}/hamlib-${PV}.tar.gz"
SRCREV = "${AUTOREV}"
SECTION = "libs"
PRIORITY = "optional"
LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=079b27cd65c86dbc1b6997ffde902735 \
                   file://LICENSE;md5=3ca1d2ad466cfd5d4ef601d0ab764517 \
                   file://COPYING.LIB;md5=b65ca9dc200648c0b04ccc472f1806e6"

DEPENDS = "perl python tcl"

PR = "r1"

EXTRA_OECONF = "--prefix=/usr/"

inherit autotools

