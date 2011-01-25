SUMMARY = "UPnP framework"
DESCRIPTION = "GUPnP is an elegant, object-oriented open source framework for creating UPnP  devices and control points, written in C using GObject and libsoup. The GUPnP API is intended to be easy to use, efficient and flexible. It provides the same set of features as libupnp, but shields the developer from most of UPnP's internals."
HOMEPAGE = "http://gupnp.org/"

LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=3bf50002aefd002f49e7bb854063f7e7 \
                    file://libgupnp/gupnp.h;beginline=6;endline=20;md5=97f61234145c37a07d3cc885d187224e"
DEPENDS = "e2fsprogs gssdp libsoup-2.4 libxml2 gobject-introspection-native"

SRC_URI = "http://gupnp.org/sites/all/files/sources/${PN}-${PV}.tar.gz"
SRC_URI[md5sum] = "42ec93968e77d91efe2f77a56c6b3f33"
SRC_URI[sha256sum] = "7b81df4b0e810b608e29dae8aed79cd1b1e71002db387de7fdb884c2ca1e77eb"

PR = "r0"

inherit autotools pkgconfig

FILES_${PN} = "${libdir}/*.so.*"
FILES_${PN}-dev += "${bindir}/gupnp-binding-tool"

SYSROOT_PREPROCESS_FUNCS += "gupnp_sysroot_preprocess"

gupnp_sysroot_preprocess () {
	install -d ${SYSROOT_DESTDIR}${STAGING_BINDIR_CROSS}/
	install -m 755 ${D}${bindir}/gupnp-binding-tool ${SYSROOT_DESTDIR}${STAGING_BINDIR_CROSS}/
}
