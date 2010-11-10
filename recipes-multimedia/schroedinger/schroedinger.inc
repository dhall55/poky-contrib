HOMEPAGE = "http://schrodinger.sourceforge.net/"
LICENSE = "MPL GPLv2 LGPLv2 MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=d91a46405fc074b88c963cc4f2a0aae9 \
                    file://COPYING.GPL;md5=e181e3b7c66f5f96921d813c1074f833 \
                    file://COPYING.LGPL;md5=38c893e21baec4cd75ad800ba9e2410a \
                    file://COPYING.MIT;md5=8b345371b3536b4ce37ead1eafc88221 \
                    file://COPYING.MPL;md5=0117647fecb9a932c25a7bbfc0333c37"

DEPENDS = "liboil orc-native orc"

PR = "r1"

SRC_URI = "http://www.diracvideo.org/download/schroedinger/${P}.tar.gz;name=schroedingertargz"
SRC_URI[schroedingertargz.md5sum] = "d67ec48b7c506db8c8b49156bf409e60"
SRC_URI[schroedingertargz.sha256sum] = "345abcaa72ff0f2e9c1075e22f7141475ee4e6eea23a7f568b69ffc13cc1c723"
SRC_URI += "file://configure.ac.patch"

EXTRA_OECONF += "STAGING_DIR=${STAGING_DIR_NATIVE}"

inherit autotools

