DESCRIPTION = "libgee is a collection library providing GObject-based interfaces \
and classes for commonly used data structures."
HOMEPAGE = "http://live.gnome.org/Libgee"
SECTION = "libs"
DEPENDS = "glib-2.0 gobject-introspection-native"
BBCLASSEXTEND = "native"
LICENSE = "LGPLv2.1+"
LIC_FILES_CHKSUM = "file://COPYING;md5=fbc093901857fcd118f065f900982c24 \
                    file://gee/map.c;beginline=8;endline=20;md5=43c733423764f0802e44117eaa0426d5"

PE = "1"

inherit autotools vala
