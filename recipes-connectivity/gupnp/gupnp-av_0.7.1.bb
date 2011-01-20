SUMMARY = "Helpers for AV applications using UPnP"
DESCRIPTION = "GUPnP-AV is a collection of helpers for building AV (audio/video) applications using GUPnP."
LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=3bf50002aefd002f49e7bb854063f7e7 \
                    file://libgupnp-av/gupnp-av.h;beginline=8;endline=22;md5=97f61234145c37a07d3cc885d187224e"
DEPENDS = "gupnp"
PR = "r0"

SRC_URI = "http://gupnp.org/sites/all/files/sources/${PN}-${PV}.tar.gz"
SRC_URI[md5sum] = "4ba8c71521916944400722687f3ae95a"
SRC_URI[sha256sum] = "70a23a7dd1e33b08e87a2f005bd8e1aa4e231524dd41b6a8eff9dc03112e6f19"

inherit autotools pkgconfig
