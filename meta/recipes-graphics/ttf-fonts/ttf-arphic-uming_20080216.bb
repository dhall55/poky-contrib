DESCRIPTION = "Unicode Mingti (printed) TrueType Font"
HOMEPAGE = "http://www.freedesktop.org/wiki/Software/CJKUnifonts"

SECTION = "x11/fonts"

# We may copy and distribute verbatim copies of this Font in any medium, \
# without restriction, since we retain this license file (ARPHICPL.TXT) \
# unaltered in all copies. See do_install().
LICENSE = "${PN}"
LIC_FILES_CHKSUM = "file://README;md5=62be011094b7865ddc4d1a648444d31a"

PR = "r0"

SRC_URI = \
"http://archive.ubuntu.com/ubuntu/pool/main/t/ttf-arphic-uming/ttf-arphic-uming_0.2.${PV}.1.orig.tar.gz;subdir=${BPN}-${PV}"
SRC_URI[md5sum] = "d219fcaf953f3eb1889399955a00379f"
SRC_URI[sha256sum] = "8038a6db9e832456d5da5559aff8d15130243be1091bf24f3243503a6f1bda98"

FILES_${PN} = "${datadir} ${sysconfdir} ${docdir}"

PACKAGES = "${PN}"
PACKAGE_ARCH = "all"

RDEPENDS = "fontconfig-utils"

# we don't need a compiler nor a c library for these fonts
INHIBIT_DEFAULT_DEPS = "1"

do_install() {
    install -d ${D}${datadir}/fonts/truetype/
    find ./ -name '*.tt[cf]' -exec install -m 0644 {} ${D}${datadir}/fonts/truetype/ \;

    install -d ${D}${sysconfdir}/fonts/conf.d/
    find ./ -name "*ttf-arphic-uming*.conf" -exec install -m 0644 {}  ${D}${sysconfdir}/fonts/conf.d/ \;

    install -d ${D}${docdir}
    install -d ${D}${docdir}/${PN}
    cp -ax license  ${D}${docdir}/${PN}/
}

pkg_postinst_${PN} () {
#!/bin/sh
if [ "x$D" != "x" ] ; then
    exit 1
fi
fc-cache
}

