DEPENDS = "gstreamer libva ffmpeg"
LICENSE = "GPLv2 | LGPLv2.1"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe"

SRC_URI = "http://www.splitted-desktop.com/~gbeauchesne/${BPN}/${BPN}-${PV}.tar.gz"
SRC_URI[md5sum] = "729d75f21df79114a8c81d896489e5ad"
SRC_URI[sha256sum] = "f1770c4537f1615701dbc845eee5732fbb1036b3acafbc7488e551fab334a31d"

inherit autotools

PR = "r0"

FILES_${PN} += "${libdir}/gstreamer-0.10/*.so"
FILES_${PN}-dbg += "${libdir}/gstreamer-0.10/.debug"
FILES_${PN}-dev += "${libdir}/gstreamer-0.10/*.la ${libdir}/gstreamer-0.10/*.a"
