require qt4.inc

DESCRIPTION = "Qt is a versatile cross-platform application framework -- this is the X11 version."
HOMEPAGE = "http://qt.nokia.com"
SECTION = "x11/libs"
DEPENDS += "virtual/libgl virtual/libx11 fontconfig libxft libxext libxrender libxrandr libxcursor"
PROVIDES += "qt4-x11"
QT4DEPENDS = ""

INC_PR = "r47"

QT_GLFLAGS ?= "${@base_contains('DISTRO_FEATURES', 'opengl', '-opengl', '-no-opengl', d)} "
QT_GLFLAGS_qemux86 = "-opengl"
QT_GLFLAGS_qemuppc = "-opengl"
QT_X11_FLAGS ?= "-no-xinerama -no-xkb"
QT_CONFIG_FLAGS += "${QT_X11_FLAGS}"
QT_BASE_LIB  ?= "libqt"

# required by kdelibs4
QT_KDE_FLAGS ?= "-accessibility -sm"
QT_DISTRO_FLAGS ?= "${QT_KDE_FLAGS}"

inherit qt4x11

do_install_append() {
  # fix pkgconfig, libtool and prl files
  sed -i -e 's#I/usr/include#Iincludedir}#g' \ 
    -e 's#Iin#I${in#g' \
    ${D}${libdir}/*.la ${D}${libdir}/*.prl ${D}${libdir}/pkgconfig/*.pc

  # QT abuses $includedir to point to its headers, which breaks pkgconfig sysroot, so
  # manually fix it up here:
  for pc in ${D}${libdir}/pkgconfig/*.pc ; do
    sed -i -e "s:prefix}include/${QT_BASE_NAME}/$(basename $pc .pc):prefix}/include:" \
      -e "s,Cflags: ,Cflags: -IP{includedir}/${QT_BASE_NAME}/$(basename $pc .pc) ," \
      -e 's:IP{:I${:g' $pc
  done
}
