SUMMARY = ""
DESCRIPTION = ""
LICENSE = "LGPLv2.1+"
LIC_FILES_CHKSUM = "file://COPYING;md5=4fbd65380cdd255951079008b364516c \
                    file://libgupnp-dlna/gupnp-dlna-discoverer.c;beginline=6;endline=20;md5=dcb953508062c2a525691fb2d497ed67"
DEPENDS = "gupnp gstreamer gst-plugins-base"
PR = "r3"

SRC_URI = "http://gupnp.org/sites/all/files/sources/${PN}-${PV}.tar.gz"

inherit autotools pkgconfig
