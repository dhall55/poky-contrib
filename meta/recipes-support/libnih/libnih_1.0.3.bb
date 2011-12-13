HOMEPAGE = "https://launchpad.net/libnih"
SUMMARY = "a small library for C application development"

LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe"

DEPENDS = "dbus expat libnih-native"
DEPENDS_virtclass-native = "dbus-native expat-native"

SRC_URI = "http://launchpad.net/libnih/1.0/${PV}/+download/${BPN}-${PV}.tar.gz \
	   file://gettext-version.patch"
SRC_URI[md5sum] = "db7990ce55e01daffe19006524a1ccb0"
SRC_URI[sha256sum] = "897572df7565c0a90a81532671e23c63f99b4efde2eecbbf11e7857fbc61f405"

inherit gettext autotools

BBCLASSEXTEND="native"