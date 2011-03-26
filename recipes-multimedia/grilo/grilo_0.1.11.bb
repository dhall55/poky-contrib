SUMMARY = "Media discovery framework"
DESCRIPTION = "Grilo is a framework focused on making media discovery and browsing easy for application developers."
HOMEPAGE = "http://live.gnome.org/Grilo"

LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=fbc093901857fcd118f065f900982c24"

DEPENDS = "glib-2.0 libxml2 gtk+ gconf-dbus libsoup-2.4"

SRC_URI[archive.md5sum] = "5be25fcc0c6d918c940664e886a3fe9e"
SRC_URI[archive.sha256sum] = "19e2803ea47cec9b3877789bca0cd5445085fd8be9ca8de70107b90434f9b76b"

PR = "r0"

inherit gnome
