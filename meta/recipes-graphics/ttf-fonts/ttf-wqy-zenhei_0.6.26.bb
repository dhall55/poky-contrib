DESCRIPTION = "WenQuanYi Zen Hei - A Hei-Ti Style Chinese font"
AUTHOR = "Qianqian Fang and The WenQuanYi Project Contributors"
HOMEPAGE = "http://wqy.sourceforge.net/en/"

SECTION = "x11/fonts"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=cf540fc7d35b5777e36051280b3a911c"

PR = "r0"

SRC_URI = "${SOURCEFORGE_MIRROR}/wqy/wqy-zenhei-${PV}-0.tar.gz"
SRC_URI[md5sum] = "bf2c1cb512606d995873bada27c777da"
SRC_URI[sha256sum] = "47355b6ec84bb309614b6d657ddfda993b96ed0be569264f82e523b254f945b2"

S = "${WORKDIR}/wqy-zenhei"

PACKAGES = "${PN}"
PACKAGE_ARCH = "all"

RDEPENDS = "fontconfig-utils"

# we don't need a compiler nor a c library for these fonts
INHIBIT_DEFAULT_DEPS = "1"

FILES_${PN} = "${datadir} ${sysconfdir}"

do_install() {
    install -d ${D}${datadir}/fonts/truetype/
    find ./ -name '*.tt[cf]' -exec install -m 0644 {} ${D}${datadir}/fonts/truetype/ \;

	install -d ${D}${sysconfdir}/fonts/conf.d/
	install -m 0644 ${S}/44-wqy-zenhei.conf ${D}${sysconfdir}/fonts/conf.d/
	install -m 0644 ${S}/66-wqy-zenhei-sharp.conf ${D}${sysconfdir}/fonts/conf.d/
}

pkg_postinst_${PN} () {
#!/bin/sh
if [ "x$D" != "x" ] ; then
    exit 1
fi
fc-cache
}
