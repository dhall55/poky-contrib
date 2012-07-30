DEFAULT_PREFERENCE = "-1"

include libxcb.inc

SRCREV = "625ed596cae6dd8175aeb6cb6f26784928042f22"
PV = "1.1.90.1+gitr${SRCPV}"
PR = "r2"

DEPENDS += "libpthread-stubs xcb-proto-native"

SRC_URI = "git://anongit.freedesktop.org/git/xcb/libxcb;protocol=git"
S = "${WORKDIR}/git"

PACKAGES =+ "libxcb-xinerama"
