SUMMARY = "Video thumbnailer"
DESCRIPTION = "This video thumbnailer can be used to create thumbnails for your video files. The thumbnailer uses ffmpeg to decode frames from the video files, so supported videoformats depend on the configuration flags of ffmpeg."
HOMEPAGE = "http://code.google.com/p/ffmpegthumbnailer/"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=393a5ca445f6965873eca0259a17f833"
SRC_URI = "http://ffmpegthumbnailer.googlecode.com/files/${PN}-${PV}.tar.gz"

DEPENDS = "ffmpeg libpng"

SRC_URI[archive.md5sum] = "a5e471c144a31067ae4e870699f451cf"
SRC_URI[archive.sha256sum] = "83cd452cdbc48df9bcfe3f5662a1ffa3b784343529baa1dd73974915a212c31f"

PR = "r0"

inherit autotools
