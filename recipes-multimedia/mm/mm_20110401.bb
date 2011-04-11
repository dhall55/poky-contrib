SUMMARY = "A BSD licensed surface/physics upnp media player"

LICENSE = "Simplified BSD"
LIC_FILES_CHKSUM = "file://README;md5=34b26b12bf909c4cdc26c17897f41f1f"

DEPENDS = "glib-2.0 clutter-1.6 clutter-box2d grilo grilo-plugins clutter-gst-1.6"
RDEPENDS_${PN} += "grilo-plugins"

SRC_URI = "http://pippin.gimp.org/${BPN}-${PV}.tar.gz \
	   file://fake-query-with-browse.patch \
	   file://debug_fixes.patch \
	   file://mm.desktop"
SRC_URI[md5sum] = "03b5fe1f21c79c8155a118fb28a0c8e1"
SRC_URI[sha256sum] = "978fda5f591af1ec853ecf77de6132d6ecd6f22daa663cb2399ef9406b6f1f30"

PR = "r2"

S = "${WORKDIR}/mm"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 mm ${D}${bindir}
    install -d ${D}${datadir}
    install -d ${D}${datadir}/applications
    install -d ${D}/${datadir}/pixmaps
    install -m 0644 ${WORKDIR}/mm.desktop ${D}${datadir}/applications
    install -m 0644 *.png ${D}/${datadir}/pixmaps
}
