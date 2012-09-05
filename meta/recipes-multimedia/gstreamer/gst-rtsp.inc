DESCRIPTION = "GStreamer RTSP server"
LICENSE = "LGPLv2"

DEPENDS = "gstreamer gst-plugins-base"

SRC_URI = "http://gstreamer.freedesktop.org/src/${PN}/${PN}-${PV}.tar.bz2"

inherit autotools
