SUMMARY = "a GLib-based library for accessing online service APIs using the GData protocol"
DESCRIPTION = "libgdata is a GLib-based library for accessing online service APIs using the protocol GData most notably, Google's services. It provides APIs to access the common Google services, and has full asynchronous support. "
HOMEPAGE = "http://live.gnome.org/libgdata"

LICENSE = "LGPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=fbc093901857fcd118f065f900982c24"

DEPENDS = "glib-2.0 libsoup-2.4 gdk-pixbuf"

SRC_URI[archive.md5sum] = "43ad483c17446dcc7d1c8d3fa49dcc90"
SRC_URI[archive.sha256sum] = "1a816dda7de8ce162e00cc1c782a5ae25230a36d56c590a67d86848058797c9f"

PR = "r0"

inherit gnome gettext
