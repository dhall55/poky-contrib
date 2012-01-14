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

SRC_URI = "${GNU_MIRROR}/guile/guile-${PV}.tar.gz \
           file://debian/0001-Fix-the-SRFI-60-copy-bit-documentation.patch \
           file://debian/0002-Define-_GNU_SOURCE-to-fix-the-GNU-kFreeBSD-build.patch \
           file://debian/0003-Include-gc.h-rather-than-gc-gc_version.h-in-pthread-.patch \
           file://opensuse/guile-64bit.patch \
           file://opensuse/guile-turn-off-gc-test.patch \
           "

SRC_URI[md5sum] = "3b8b4e1083037f29d2c4704a6d55f2a8"
SRC_URI[sha256sum] = "a53b21159befe3e89bbaca71e9e62cf00af0f49fcca297c407944b988d59eb08"

PR = "r0"

inherit autotools gettext

DEPENDS = "libunistring bdwgc gmp"
BBCLASSEXTEND = "native nativesdk"

do_configure_prepend() {
	mkdir -p po
}

do_install_append_virtclass-native() {
	install -m 0755  ${D}${bindir}/guile ${D}${bindir}/${HOST_SYS}-guile
}

export GUILE_FOR_BUILD=${BUILD_SYS}-guile
