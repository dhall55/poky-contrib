DESCRIPTION = "Spidermonkey: a javascript engine written in C"
HOMEPAGE = "http://www.mozilla.org/js/spidermonkey/"
SECTION = "libs"

# the package is licensed under either of the following
LICENSE = "MPL-1 | GPLv2+ | LGPLv2.1+"
LIC_FILES_CHKSUM = "file://jsapi.h;beginline=4;endline=39;md5=347c6bbf4fb4547de1fa5ad830030063"
PR = "r0"

DEPENDS = "nspr"

SRC_URI = "http://ftp.mozilla.org/pub/mozilla.org/js/js185-1.0.0.tar.gz \
           file://link_with_gcc.patch \
           file://usepic.patch \
          "

SRC_URI[md5sum] = "a4574365938222adca0a6bd33329cb32"
SRC_URI[sha256sum] = "5d12f7e1f5b4a99436685d97b9b7b75f094d33580227aa998c406bbae6f2a687"

S = "${WORKDIR}/${PN}-${PV}/js/src"

inherit autotools

# Use the configure and avoid autoconf as v2.13 is mandatory
do_configure_prepend() {
	rm -f ${S}/configure.in
}

EXTRA_OEMAKE = "'CC=${CC}' 'LD=${LD}' 'XCFLAGS=${CFLAGS}' 'XLDFLAGS=${LDFLAGS} -Wl,-soname=libjs' \
                'BUILD_CC=${BUILD_CC}' 'BUILD_CFLAGS=${BUILD_CFLAGS}' 'BUILD_LDFLAGS=${BUILD_LDFLAGS}'"

EXTRA_OECONF = '--with-nspr-libs="-lplds4 -lplc4 -lnspr4" \
                --prefix=/usr'

PARALLEL_MAKE = ""

