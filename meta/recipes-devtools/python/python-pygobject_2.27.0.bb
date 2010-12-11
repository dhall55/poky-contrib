DESCRIPTION = "Python GObject bindings"
SECTION = "devel/python"
LICENSE = "LGPLv2.1"
LIC_FILES_CHKSUM = "file://COPYING;md5=a916467b91076e631dd8edb7424769c7"
DEPENDS = "python-pygobject-native-${PV} glib-2.0"
PR = "r0"

MAJ_VER = "${@bb.data.getVar('PV',d,1).split('.')[0]}.${@bb.data.getVar('PV',d,1).split('.')[1]}"

SRC_URI = "ftp://ftp.gnome.org/pub/GNOME/sources/pygobject/${MAJ_VER}/pygobject-${PV}.tar.bz2 \
	   file://generate-constants.patch"
S = "${WORKDIR}/pygobject-${PV}"

FILESPATH = "${FILE_DIRNAME}/python-pygobject:${FILE_DIRNAME}/files"

inherit autotools distutils-base pkgconfig

# necessary to let the call for python-config succeed
export BUILD_SYS
export HOST_SYS
export STAGING_INCDIR
export STAGING_LIBDIR

PACKAGES += "${PN}-lib"

RDEPENDS_${PN} += "python-textutils"

FILES_${PN} = "${libdir}/python*"
FILES_${PN}-lib = "${libdir}/lib*.so.*"
FILES_${PN}-dev += "${bindir} ${datadir}"
FILES_${PN}-dbg += "${libdir}/.debug"
