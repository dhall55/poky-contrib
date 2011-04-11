SUMMARY = "Resource discovery and announcement over SSDP"
DESCRIPTION = "GSSDP implements resource discovery and announcement over SSDP (Simpe Service Discovery Protocol)."
LICENSE = "LGPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=3bf50002aefd002f49e7bb854063f7e7"
DEPENDS = "glib-2.0 libsoup-2.4 libglade"

SRC_URI = "http://gupnp.org/sites/all/files/sources/${PN}-${PV}.tar.gz \
           file://introspection.patch"

SRC_URI[md5sum] = "f60806a6b01748606d20649162bf2b59"
SRC_URI[sha256sum] = "eaa080e86bc7d1204c5bf96980aaca055d823b0d12b0e1485bb15322b361c9c0"

inherit autotools pkgconfig

PACKAGES =+ "gssdp-tools"

FILES_gssdp-tools = "${bindir}/gssdp* ${datadir}/gssdp/*.glade"

EXTRA_OECONF = "--disable-introspection"

PR = "r0"


