SUMMARY = "Media discovery framework"
DESCRIPTION = "Grilo is a framework focused on making media discovery and browsing easy for application developers."
HOMEPAGE = "http://live.gnome.org/Grilo"

LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=fbc093901857fcd118f065f900982c24"

DEPENDS = "glib-2.0 libxml2 gtk+ gconf-dbus libsoup-2.4 grilo gupnp gupnp-av sqlite3 libgcrypt"

SRC_URI[archive.md5sum] = "3c838eb782f5b5365e6c24a3b8ec4a71"
SRC_URI[archive.sha256sum] = "2844356e5c7f8125704cf4d0846290c5e793cb5affbbcb2dc9f175e543a1d682"

PR = "r2"

inherit gnome

SRC_URI += "file://0001-upnp-poll-for-presence-of-upnp-media-server.patch"

FILES_${PN} += " ${libdir}/grilo-0.1/*.so"
FILES_${PN}-dev += " ${libdir}/grilo-0.1/*.la ${libdir}/grilo-0.1/*.a"
FILES_${PN}-dbg += " ${libdir}/grilo-0.1/.debug/"
