DESCRIPTION = "Matchbox Desktop"
HOMEPAGE = "http://matchbox-project.org/"
BUGTRACKER = "http://bugzilla.openedhand.com/"

LICENSE = "GPLv2+ & LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=94d55d512a9ba36caa9b7df079bae19f \
                    file://src/desktop.c;endline=20;md5=36c9bf295e6007f3423095f405af5a2d \
                    file://src/main.c;endline=19;md5=2044244f97a195c25b7dc602ac7e9a00"

DEPENDS = "gtk+3 startup-notification dbus"
SECTION = "x11/wm"
SRCREV = "fde3c4fe6a8cee59a1ae5653b3905523f6629e0f"
PV = "3.0+git${SRCPV}"
PR = "r0"

SRC_URI = "git://git.yoctoproject.org/${BPN}-2;protocol=git"

EXTRA_OECONF = "--enable-startup-notification --with-dbus"

S = "${WORKDIR}/git"

inherit autotools pkgconfig
