SRC_URI = "${GNOME_MIRROR}/gobject-introspection/0.6/${BPN}-${PV}.tar.bz2 \
	   file://configure.patch \
	   file://fixpaths.patch \
           file://pathfix.patch"

SRC_URI_virtclass-native = "${GNOME_MIRROR}/gobject-introspection/0.6/${BPN}-${PV}.tar.bz2 \
			    file://pathfix.patch"

LICENSE = "GPLv2+ & LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=90d577535a3898e1ae5dbf0ae3509a8c \
                    file://COPYING.GPL;md5=94d55d512a9ba36caa9b7df079bae19f \
                    file://COPYING.LGPL;md5=3bf50002aefd002f49e7bb854063f7e7"
PR = "r2"

EXTRA_OECONF = "--disable-tests"

DEPENDS = "libffi gobject-introspection-native glib-2.0"
DEPENDS_virtclass-native = "libffi-native python-native bison-native flex-native glib-2.0-native"

inherit autotools

TARGET_CFLAGS += "-I${STAGING_INCDIR}/python2.6"

do_configure_prepend () {
	echo "EXTRA_DIST = " > ${S}/gtk-doc.make
}

BBCLASSEXTEND = "native"
