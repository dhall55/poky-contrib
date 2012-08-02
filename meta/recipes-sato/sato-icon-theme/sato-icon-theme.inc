DESCRIPTION = "Sato Icon Theme"
HOMEPAGE = "http://www.o-hand.com"
BUGTRACKER = "http://bugzilla.openedhand.com/"

LICENSE = "CC-BY-SA-3.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=56a830bbe6e4697fe6cbbae01bb7c2b2"

SECTION = "x11"
DEPENDS = "gtk+-native"

inherit autotools pkgconfig allarch

FILES_${PN} += "${datadir}"

EXTRA_OECONF += "--with-iconmap=${STAGING_LIBDIR_NATIVE}/../libexec/icon-name-mapping"

#explictly setting "Sato" as default icon theme to avoid icon missing due to
#tricky race condition
pkg_postinst_${PN} () {
        gtk-update-icon-cache -q $D/usr/share/icons/Sato
        if [ ! -d $D/etc/gtk-2.0 ]; then
            mkdir -p $D/etc/gtk-2.0
        fi
        echo 'gtk-icon-theme-name = "Sato"' >> $D/etc/gtk-2.0/gtkrc
}
