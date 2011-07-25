DESCRIPTION = "Platform independent non-GUI operating system facilities."
HOMEPAGE = "https://www.mozilla.org/projects/nspr"
LICENSE = "MPL1.1 & GPL & LGPL"
LIC_FILES_CHKSUM = "file://pr/src/nspr.rc;md5=10212f88345baaa955c3b6a824b928d4"

PR = "r0"

DEPENDS = "nspr-tools-native"

S = "${WORKDIR}/${P}/mozilla/nsprpub"

inherit autotools

EXTRA_OECONF = "\
	--enable-ipv6 \
	--with-mozilla \
	--includedir=${includedir}/mozilla/nspr \
	"

TARGET_CC_ARCH += "${LDFLAGS}"

do_compile_prepend() {
    cp ${STAGING_BINDIR_NATIVE}/${P}/now config/now
    touch config/now

    cp ${STAGING_BINDIR_NATIVE}/${P}/nsinstall config/nsinstall
    touch config/nsinstall
}

do_install_prepend() {
    cp ${STAGING_BINDIR_NATIVE}/${P}/now config/now
    touch config/now

    cp ${STAGING_BINDIR_NATIVE}/${P}/nsinstall config/nsinstall
    touch config/nsinstall
}

LEAD_SONAME = "libnspr4.so"
