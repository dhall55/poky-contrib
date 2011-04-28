SRC_URI_append_build-darwin = "   file://non-gnu.patch "
RDEPENDS_${PN} = "diffstat-native patch-native bzip2-native util-linux-native"

INHIBIT_AUTOTOOLS_DEPS = "1"

inherit native

PATCHTOOL = "patch"
EXTRA_OECONF = "--disable-nls"
EXTRA_OECONF_build-darwin = "--disable-nls --without-date --without-getopt"

do_configure () {
	oe_runconf
}
