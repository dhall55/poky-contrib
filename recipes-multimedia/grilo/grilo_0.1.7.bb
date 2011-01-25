SUMMARY = "Media discovery framework"
DESCRIPTION = "Grilo is a framework focused on making media discovery and browsing easy for application developers."
HOMEPAGE = "http://live.gnome.org/Grilo"

LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=fbc093901857fcd118f065f900982c24"

DEPENDS = "glib-2.0 libxml2 gtk+ gconf-dbus libsoup-2.4"

SRC_URI[archive.md5sum] = "abb06e83a579eef84f2993c900c929c3"
SRC_URI[archive.sha256sum] = "b8db743a570471260b1d0bc9e4922ea818103ce6f3a8bd36e936f7412fc7a2ab"

PR = "r0"

inherit gnome
