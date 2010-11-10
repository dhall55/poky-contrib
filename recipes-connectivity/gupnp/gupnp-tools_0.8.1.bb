DESCRIPTION = "Tools for GUPnP"
LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe \
                    file://src/av-cp/main.c;beginline=6;endline=19;md5=957b9dd69975d5414473b1251aab0d8e"
DEPENDS = "gupnp gtk+ libglade gnome-icon-theme"
PR = "r1"

SRC_URI = "http://gupnp.org/sites/all/files/sources/${PN}-${PV}.tar.gz"

inherit autotools pkgconfig
