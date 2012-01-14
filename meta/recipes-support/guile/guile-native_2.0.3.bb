SUMMARY = "Guile is the GNU Ubiquitous Intelligent Language for Extensions."
DESCRIPTION = "Guile is the GNU Ubiquitous Intelligent Language for Extensions,\
 the official extension language for the GNU operating system.\
 Guile is a library designed to help programmers create flexible applications.\
 Using Guile in an application allows the application's functionality to be\
 extended by users or other programmers with plug-ins, modules, or scripts.\
 Guile provides what might be described as "practical software freedom,"\
 making it possible for users to customize an application to meet their\
 needs without digging into the application's internals."

HOMEPAGE = "http://www.gnu.org/software/guile/"
SECTION = "devel"
LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://COPYING;md5=d32239bcb673463ab874e80d47fae504" 

SRC_URI = "${GNU_MIRROR}/guile/guile-${PV}.tar.gz"

SRC_URI[md5sum] = "3b8b4e1083037f29d2c4704a6d55f2a8"
SRC_URI[sha256sum] = "a53b21159befe3e89bbaca71e9e62cf00af0f49fcca297c407944b988d59eb08"

PR = "r0"

inherit autotools gettext

DEPENDS = "libunistring-native bdwgc-native gmp-native"

do_configure_prepend() {
	mkdir -p po
}
