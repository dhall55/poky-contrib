DESCRIPTION = "Tools for GUPnP"
LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe \
                    file://src/av-cp/main.c;beginline=6;endline=19;md5=957b9dd69975d5414473b1251aab0d8e"
DEPENDS = "gupnp gtk+ libglade gnome-icon-theme"
PR = "r0"

SRC_URI = "http://gupnp.org/sites/all/files/sources/${PN}-${PV}.tar.gz"

SRC_URI[md5sum] = "d8a44a8c19b1cc10b8e5508448d8493f"
SRC_URI[sha256sum] = "3b46a76fcbb0188b8d2c406e514edc7662d65f48774c81e5a19f93d7706db302"

inherit autotools pkgconfig
