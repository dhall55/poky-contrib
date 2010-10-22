inherit gnome vala autotools gtk-icon-cache update-rc.d

DESCRIPTION = "Collection of DLNA[1] (UPnP[2] AV) devices, implemented through a plug-in mechanism."
SECTION = "network/multimedia"
DEPENDS = "glib-2.0 gupnp gupnp-av gupnp-dlna gstreamer gst-plugins-base sqlite3 libsoup-2.4 libgee gobject-introspection-native"

# This doesn't seem to work...
RDEPENDS = "gst-meta-audio gst-meta-video gst-meta-base gst-plugins-base-decodebin2 gst-plugins-base-videorate gst-plugins-base-videoscale gst-plugins-base-ffmpegcolorspace gst-ffmpeg gst-plugins-ugly-lame gst-plugins-base-audioconvert gst-plugins-ugly-mpeg2dec gst-plugins-base-audiotestsrc gst-plugins-base-audiorate gst-plugins-base-videotestsrc"

HOMEPAGE = "http://live.gnome.org/Rygel"
LICENSE = "LGPLv2"
PR="r3"

SRC_URI += "file://configure-fix.patch \
            file://rygel.conf \
            file://rygel.init"

EXTRA_OECONF = "--disable-vala --disable-tracker-plugin"

do_install_append() {
  install -d ${D}/home/root/.config
  install -m 0755 ${WORKDIR}/rygel.conf ${D}/home/root/.config/rygel.conf
}

FILES_${PN} += "${libdir}/rygel-1.0/librygel*.so ${datadir}/dbus-1/ /home/root/.config/"
FILES_${PN}-dbg += "${libdir}/rygel-1.0/.debug/"

INITSCRIPT_NAME = "rygel"

do_install_append() {
    install -d ${D}${sysconfdir}/init.d
    install -m 0755 ${WORKDIR}/rygel.init ${D}${sysconfdir}/init.d/rygel
}
