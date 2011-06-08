DEPENDS = "qt-x11-free-native freetype virtual/libx11 libxmu libxft libxext libxrender libxrandr libxcursor  virtual/libgl"
PROVIDES = "qt3x11"
PR = "r0"

PREFERRED_VERSION_qt-x11-free = 3.3.7
LIC_FILES_CHKSUM = "file://LICENSE.GPL;md5=b07b0d5ac6b1822effe47173a1744433 \
                    file://LICENSE.QPL;md5=b81b6b6fc04ed873adde5aa901c0613b"

SRC_URI = "ftp://ftp.trolltech.com/qt/source/qt-x11-free-${PV}.tar.bz2 \
	   file://configure.patch \
	   file://no-examples.patch \
           file://gcc4_1-HACK.patch \
           file://qt3-cstddef.patch"

require qt-x11-free-common.inc

SRC_URI[md5sum] = "655e21cf6a7e66daf8ec6ceda81aae1e"
SRC_URI[sha256sum] = "48c05b501029f0640db665fbc7f981a0efbf69ad3cf87a43c5eea4872f4f7ba1"
