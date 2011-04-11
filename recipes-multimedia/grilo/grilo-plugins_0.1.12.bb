SUMMARY = "Media discovery framework"
DESCRIPTION = "Grilo is a framework focused on making media discovery and browsing easy for application developers."
HOMEPAGE = "http://live.gnome.org/Grilo"

LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=fbc093901857fcd118f065f900982c24"

DEPENDS = "glib-2.0 libxml2 gtk+ gconf-dbus libsoup-2.4 grilo gupnp gupnp-av sqlite3 libgcrypt"

SRC_URI[archive.md5sum] = "b2b537da034fca523ef89f8e3679a3c6" 
SRC_URI[archive.sha256sum] = "94c4b9968a4720928d6aa88d841f2fe33275b864de6245740cb34421e38349f1" 

PR = "r0"

inherit gnome

SRC_URI += "file://0001-upnp-poll-for-presence-of-upnp-media-server.patch"

FILES_${PN} += " ${libdir}/grilo-0.1/*.so ${datadir}/grilo-0.1/plugins/*.xml"
FILES_${PN}-dev += " ${libdir}/grilo-0.1/*.la ${libdir}/grilo-0.1/*.a"
FILES_${PN}-dbg += " ${libdir}/grilo-0.1/.debug/"
