DESCRIPTION = "Various benchmarning tests for X"
HOMEPAGE = "http://www.o-hand.com"
SECTION = "devel"
LICENSE = "GPLv2 & LGPLv2.1 "
DEPENDS = "pango libxext libxft virtual/libx11 gtk+"
PV = "0.0+svnr${SRCREV}"
PR = "r0"

inherit autotools

SRC_URI = "svn://svn.o-hand.com/repos/misc/trunk;module=fstests;proto=http"

S = "${WORKDIR}/fstests/tests"

do_install() {
    install -d ${D}${bindir}
    find . -name "test-*" -type f -perm -755 -exec install -m 0755 {} ${D}${bindir} \;   
}


LIC_FILES_CHKSUM = " \
    file://video/COPYING;md5=ac14b7ca45afea5af040da54db270eb0 \
    file://zaurusd/COPYING;md5=94d55d512a9ba36caa9b7df079bae19f \
    file://libowl/COPYING;md5=94d55d512a9ba36caa9b7df079bae19f \
    file://libowl-av/COPYING;md5=ac14b7ca45afea5af040da54db270eb0 \
    file://dbus-wait/COPYING;md5=b234ee4d69f5fce4486a80fdaf4a4263 \
    file://wiicursor/COPYING;md5=59530bdf33659b29e73d4adb9f9f6552 \
    file://qemu-packaging/poky-depends/debian/copyright;md5=6e91cad3fbf26d94c7005d15d4022366 \
    file://qemu-packaging/qemu/debian/copyright;md5=e7c6c7efe2b57f5cebc28660301df3c1 \
    file://qemu-packaging/poky-scripts/debian/copyright;md5=ec1e7f9274e0e2bb38a527ab2364b34d \
    file://gaku/COPYING;md5=59530bdf33659b29e73d4adb9f9f6552 \
    file://grandr-applet/COPYING;md5=94d55d512a9ba36caa9b7df079bae19f \
    file://screenshot/COPYING;md5=94d55d512a9ba36caa9b7df079bae19f \
    file://exmap-console/COPYING;md5=eb723b61539feef013de476e68b5c50a \
    file://test-xvideo/COPYING;md5=59530bdf33659b29e73d4adb9f9f655 "

