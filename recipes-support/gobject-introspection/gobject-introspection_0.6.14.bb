SRC_URI = "${GNOME_MIRROR}/gobject-introspection/0.6/${BPN}-${PV}.tar.bz2 \
	   file://configure.patch \
	   file://fixpaths.patch \
           file://pathfix.patch"

SRC_URI_virtclass-native = "${GNOME_MIRROR}/gobject-introspection/0.6/${BPN}-${PV}.tar.bz2 \
			    file://pathfix.patch"

LICENSE = "GPLv2+ & LGPLv2+"
PR = "r0"

EXTRA_OECONF = "--disable-tests"

DEPENDS = "libffi python-native gobject-introspection-native"
DEPENDS_virtclass-native = "libffi-native python-native"

inherit autotools

TARGET_CFLAGS += "-I${STAGING_INCDIR}/python2.6"

do_configure_prepend () {
	echo "EXTRA_DIST = " > ${S}/gtk-doc.make
}

BBCLASSEXTEND = "native"
