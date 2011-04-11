DESCRIPTION = "gvfs is a vfs abstraction library"
SECTION = "libs"
DEPENDS = "glib-2.0 fuse avahi hal gconf"
LICENSE = "LGPLv2.1+"
LIC_FILES_CHKSUM = "file://COPYING;md5=3bf50002aefd002f49e7bb854063f7e7" 

EXTRA_OECONF = "--disable-gphoto2 --disable-cdda --disable-obexftp --disable-keyring --disable-samba --disable-archive --disable-bash-completion"

FILES_${PN} += "${libdir}/gio/modules/*.so ${datadir}/dbus-1/"

inherit autotools
