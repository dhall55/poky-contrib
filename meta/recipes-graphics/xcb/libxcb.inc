SUMMARY = "XCB: The X protocol C binding library"
DESCRIPTION = "The X protocol C-language Binding (XCB) is a replacement \
for Xlib featuring a small footprint, latency hiding, direct access to \
the protocol, improved threading support, and extensibility."
HOMEPAGE = "http://xcb.freedesktop.org"
BUGTRACKER = "https://bugs.freedesktop.org/enter_bug.cgi?product=XCB"

BBCLASSEXTEND = "native nativesdk"

SECTION = "x11/libs"
LICENSE = "MIT-X"

PARALLEL_MAKE = ""
DEPENDS = "xcb-proto xproto libxau libxslt-native xcb-proto-native"
# DEPENDS += "xsltproc-native gperf-native"

SRC_URI = "http://xcb.freedesktop.org/dist/libxcb-${PV}.tar.bz2"
#           file://xcbincludedir.patch"

PKGSUFFIX = ""
PKGSUFFIX_virtclass-nativesdk = "-nativesdk"

PACKAGES =+ "${BPN}${PKGSUFFIX}-composite ${BPN}${PKGSUFFIX}-damage \
             ${BPN}${PKGSUFFIX}-dpms ${BPN}${PKGSUFFIX}-glx \
             ${BPN}${PKGSUFFIX}-randr ${BPN}${PKGSUFFIX}-record \
             ${BPN}${PKGSUFFIX}-render ${BPN}${PKGSUFFIX}-res \
             ${BPN}${PKGSUFFIX}-screensaver ${BPN}${PKGSUFFIX}-shape \
             ${BPN}${PKGSUFFIX}-shm ${BPN}${PKGSUFFIX}-sync \
             ${BPN}${PKGSUFFIX}-xevie ${BPN}${PKGSUFFIX}-xf86dri \
             ${BPN}${PKGSUFFIX}-xfixes ${BPN}${PKGSUFFIX}-xlib \
             ${BPN}${PKGSUFFIX}-xprint ${BPN}${PKGSUFFIX}-xtest \
             ${BPN}${PKGSUFFIX}-xv ${BPN}${PKGSUFFIX}-xvmc \
             ${BPN}${PKGSUFFIX}-dri2"

FILES_${PN} = "${libdir}/libxcb.so.*"
#FILES_${PN}-dev = "${libdir}/libxcb.* ${libdir}/pkgconfig/*.pc ${includedir}/xcb/*.h"
FILES_${BPN}${PKGSUFFIX}-dri2 = "${libdir}/libxcb-dri2.so.*"
FILES_${BPN}${PKGSUFFIX}-composite = "${libdir}/libxcb-composite.so.*"
FILES_${BPN}${PKGSUFFIX}-damage = "${libdir}/libxcb-damage.so.*"
FILES_${BPN}${PKGSUFFIX}-dpms = "${libdir}/libxcb-dpms.so.*"
FILES_${BPN}${PKGSUFFIX}-glx = "${libdir}/libxcb-glx.so.*"
FILES_${BPN}${PKGSUFFIX}-randr = "${libdir}/libxcb-randr.so.*"
FILES_${BPN}${PKGSUFFIX}-record = "${libdir}/libxcb-record.so.*"
FILES_${BPN}${PKGSUFFIX}-render = "${libdir}/libxcb-render.so.*"
FILES_${BPN}${PKGSUFFIX}-res = "${libdir}/libxcb-res.so.*"
FILES_${BPN}${PKGSUFFIX}-screensaver = "${libdir}/libxcb-screensaver.so.*"
FILES_${BPN}${PKGSUFFIX}-shape = "${libdir}/libxcb-shape.so.*"
FILES_${BPN}${PKGSUFFIX}-shm = "${libdir}/libxcb-shm.so.*"
FILES_${BPN}${PKGSUFFIX}-sync = "${libdir}/libxcb-sync.so.*"
FILES_${BPN}${PKGSUFFIX}-xevie = "${libdir}/libxcb-xevie.so.*"
FILES_${BPN}${PKGSUFFIX}-xf86dri = "${libdir}/libxcb-xf86dri.so.*"
FILES_${BPN}${PKGSUFFIX}-xfixes = "${libdir}/libxcb-xfixes.so.*"
FILES_${BPN}${PKGSUFFIX}-xinerama = "${libdir}/libxcb-xinerama.so.*"
FILES_${BPN}${PKGSUFFIX}-xlib = "${libdir}/libxcb-xlib.so.*"
FILES_${BPN}${PKGSUFFIX}-xprint = "${libdir}/libxcb-xprint.so.*"
FILES_${BPN}${PKGSUFFIX}-xtest = "${libdir}/libxcb-xtest.so.*"
FILES_${BPN}${PKGSUFFIX}-xv = "${libdir}/libxcb-xv.so.*"
FILES_${BPN}${PKGSUFFIX}-xvmc = "${libdir}/libxcb-xvmc.so.*"

inherit autotools pkgconfig pythonnative

# XCBPROTO_XCBINCLUDEDIR is setup based on `pkg-config --variable=xcbincludedir xcb-proto`
# but the xcbincludedir variable doesn't point into the staging area, so it needs some
# tweeking here:
do_configure_prepend () {
    sed -i "s|XCBPROTO_XCBINCLUDEDIR=|XCBPROTO_XCBINCLUDEDIR=${STAGING_DIR_HOST}/|" \
        ${S}/configure.ac
    sed -i "s|XCBPROTO_XCBPYTHONDIR=|XCBPROTO_XCBPYTHONDIR=${STAGING_DIR_HOST}/|" \
        ${S}/configure.ac
}
