#
# Copyright (C) 2010 Intel Corporation.
#
require recipes-sato/images/poky-image-sato.bb

IMAGE_INSTALL += "rygel gupnp-tools gst-meta-audio gst-meta-video gst-meta-base gnome-icon-theme gst-plugins-base-decodebin2 gst-plugins-base-videorate gst-plugins-base-videoscale gst-plugins-base-ffmpegcolorspace gst-ffmpeg gst-plugins-ugly-lame gst-plugins-base-audioconvert gst-plugins-ugly-mpeg2dec gst-plugins-base-audiotestsrc gst-plugins-base-audiorate gst-plugins-base-videotestsrc gst-plugins-ugly-mad gst-plugins-bad-faac gst-plugins-base-vorbis gst-plugins-base-theora gst-plugins-good-matroska gst-plugins-base-ogg"

LICENSE = "MIT"
