SUMMARY = "Media discovery framework"
DESCRIPTION = "Grilo is a framework focused on making media discovery and browsing easy for application developers."
HOMEPAGE = "http://live.gnome.org/Grilo"

LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=fbc093901857fcd118f065f900982c24"

DEPENDS = "glib-2.0 libxml2 gtk+ gconf-dbus libsoup-2.4"

SRC_URI[archive.md5sum] = "a2e36b3b7214ad73bc7d703e23130565"
SRC_URI[archive.sha256sum] = "db86039b2fd4996a40ac6d8b8e11d8fbe5a47742c0cb915022ffdc636ea07f50"

PR = "r0"

inherit gnome
