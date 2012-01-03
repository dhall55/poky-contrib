HOMEPAGE = "https://launchpad.net/upstart"
SUMMARY = "event-based init daemon"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe"

DEPENDS = "dbus udev libnih libnih-native"

SRC_URI = "http://launchpad.net/upstart/1.x/${PV}/+download/${BPN}-${PV}.tar.gz"
SRC_URI[md5sum] = "3aa9ddf8459b56547a6238aa77c61815"
SRC_URI[sha256sum] = "d2b606217bdeae1cfc58193b9cbba58e30c4ee8780fd808a602bfd82c19a0ff2"

inherit gettext autotools update-alternatives

ALTERNATIVE_NAME = "init"
ALTERNATIVE_LINK = "${base_sbindir}/init"
ALTERNATIVE_PATH = "${base_sbindir}/init.upstart"
ALTERNATIVE_PRIORITY = "60"

# autotools set prefix to /usr, however we want init in /sbin
bindir = "${base_bindir}"
sbindir = "${base_sbindir}"

PACKAGES =+ "${PN}-tools"
# These binaries aren't required but are useful for debugging etc so put them
# in a separate package
FILES_${PN}-tools = "${bindir}/init-checkconf ${bindir}/initctl2dot"
