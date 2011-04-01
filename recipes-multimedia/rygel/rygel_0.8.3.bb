inherit gnome vala autotools gtk-icon-cache update-rc.d

DESCRIPTION = "Collection of DLNA[1] (UPnP[2] AV) devices, implemented through a plug-in mechanism."
SECTION = "network/multimedia"
DEPENDS = "glib-2.0 gupnp gupnp-av gupnp-dlna gstreamer gst-plugins-base sqlite3 libsoup-2.4 libgee gobject-introspection-native"

# This doesn't seem to work...
RDEPENDS = "gst-meta-audio gst-meta-video gst-meta-base gst-plugins-base-decodebin2 gst-plugins-base-videorate gst-plugins-base-videoscale gst-plugins-base-ffmpegcolorspace gst-ffmpeg gst-plugins-ugly-lame gst-plugins-base-audioconvert gst-plugins-ugly-mpeg2dec gst-plugins-base-audiotestsrc gst-plugins-base-audiorate gst-plugins-base-videotestsrc gst-plugins-good-souphttpsrc"

HOMEPAGE = "http://live.gnome.org/Rygel"
LICENSE = "LGPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=3bf50002aefd002f49e7bb854063f7e7 \
                    file://src/rygel/rygel-main.vala;beginline=9;endline=22;md5=c00a3b21ab9237b97063b8bbe3747ef8"
SRC_URI[archive.md5sum] = "dadd1bd3968ead6456950a465af89f7c"
SRC_URI[archive.sha256sum] = "7a001cf578e8b84408ddca43c24fb9392130f982527de5c90042d6c6a84e2ab0"

PR="r1"

SRC_URI += "file://configure-fix.patch \
            file://rygel.conf \
            file://rygel.init"

EXTRA_OECONF = "--disable-vala --disable-tracker-plugin --disable-media-export-plugin"

do_install_append() {
  install -m 0755 ${WORKDIR}/rygel.conf ${D}/etc/rygel.conf
}

FILES_${PN} += "${libdir}/rygel-1.0/librygel*.so ${datadir}/dbus-1/ ${sysconfdir}/rygel.conf"
FILES_${PN}-dbg += "${libdir}/rygel-1.0/.debug/"

INITSCRIPT_NAME = "rygel"

do_install_append() {
    install -d ${D}${sysconfdir}/init.d
    cat ${WORKDIR}/rygel.init | sed -e 's,/usr/bin,${bindir},g' > ${D}${sysconfdir}/init.d/rygel
    chmod 755 ${D}${sysconfdir}/init.d/rygel
}
