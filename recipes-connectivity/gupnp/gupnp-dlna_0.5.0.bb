SUMMARY = "A utility library for various DLNA-related functionality useful for DLNA MediaServer implementations."
HOMEPAGE = "http://www.gupnp.org/"

LICENSE = "LGPLv2.1+"
LIC_FILES_CHKSUM = "file://COPYING;md5=4fbd65380cdd255951079008b364516c \
                    file://libgupnp-dlna/gupnp-dlna-discoverer.c;beginline=6;endline=20;md5=dcb953508062c2a525691fb2d497ed67"
		    
DEPENDS = "gupnp gstreamer gst-plugins-base"
PR = "r0"

SRC_URI = "http://gupnp.org/sites/all/files/sources/${PN}-${PV}.tar.gz"

SRC_URI[md5sum] = "c97ffbada5cb9f700d910995fab6ab46"
SRC_URI[sha256sum] = "35e18e21cd6f0031673c323aaeab340aa301d0bee4bedc0b889a76d661cb90e9"

inherit autotools pkgconfig
