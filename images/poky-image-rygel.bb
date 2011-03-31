#
# Copyright (C) 2010 Intel Corporation.
#
require recipes-sato/images/poky-image-sato.bb

SRC_URI = "file://interfaces"
SRC_URI_append_beagleboard = " file://inittab"

IMAGE_INSTALL += "rygel gupnp-tools gst-meta-audio gst-meta-video gst-meta-base gnome-icon-theme gst-plugins-base-decodebin2 gst-plugins-base-videorate gst-plugins-base-videoscale gst-plugins-base-ffmpegcolorspace gst-ffmpeg gst-plugins-ugly-lame gst-plugins-base-audioconvert gst-plugins-ugly-mpeg2dec gst-plugins-base-audiotestsrc gst-plugins-base-audiorate gst-plugins-base-videotestsrc gst-plugins-ugly-mad gst-plugins-bad-faac gst-plugins-base-vorbis gst-plugins-base-theora gst-plugins-good-matroska gst-plugins-base-ogg gst-plugins-good-qtdemux gst-plugins-good-souphttpsrc"

IMAGE_INSTALL_append_sugarbay = " gstreamer-vaapi"
IMAGE_INSTALL_append_crownbay = " gstreamer-vaapi"

LICENSE = "MIT"

PR = "r2"

ROOTFS_POSTPROCESS_COMMAND_append = "setup_target_image ; "
ROOTFS_POSTPROCESS_COMMAND_append_beagleboard = "setup_target_image_bb ; "

setup_target_image() {
	# Set up ethernet interface as static and auto up
        install -m 0644 ${WORKDIR}/interfaces ${IMAGE_ROOTFS}/etc/network/interfaces
}

# For beagleboard only
setup_target_image_bb() {
	# Force init 3 as default
        install -m 0644 ${WORKDIR}/inittab ${IMAGE_ROOTFS}/etc/inittab
}

