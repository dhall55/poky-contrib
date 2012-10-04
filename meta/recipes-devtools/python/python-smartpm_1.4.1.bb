SUMMARY = "The Smart Package Manager"

DESCRIPTION = "The Smart Package Manager project has the ambitious objective of creating \
smart and portable algorithms for solving adequately the problem of managing software \
upgrades and installation. This tool works in all major distributions and will bring \
notable advantages over native tools currently in use (APT, APT-RPM, YUM, URPMI, etc)."

HOMEPAGE = "http://smartpm.org/"
SECTION = "devel/python"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://LICENSE;md5=393a5ca445f6965873eca0259a17f833"

DEPENDS = "python rpm"
PR = "r0"
SRCNAME = "smart"

SRC_URI = "\
     http://launchpad.net/smart/trunk/1.4.1/+download/smart-1.4.1.tar.bz2 \
     file://smartpm-rpm5-nodig.patch \
"

SRC_URI[md5sum] = "573ef32ba177a6b3c4bf7ef04873fcb6"
SRC_URI[sha256sum] = "b1d519ddb43d60f293b065c28870a5d9e8b591cd49e8c68caea48ace91085eba"
S = "${WORKDIR}/${SRCNAME}-${PV}"

# Options - rpm, qt4, gtk
PACKAGECONFIG ??= "rpm"

rpm-rdep = "python-smartpm-backend-rpm"
qt-rdep = "python-smartpm-interface-qt4"
gtk-rdep = "python-smartpm-interface-gtk"

rpm-rdep_virtclass-native = ""
qt-rdep_virtclass-native = ""
gtk-rdep_virtclass-native = ""

PACKAGECONFIG[rpm] = ",,rpm,${rpm-rdep}"
PACKAGECONFIG[qt4] = ",,qt4-x11,${qt-rdep}"
PACKAGECONFIG[gtk] = ",,gtk+,${gtk-rdep}"

inherit distutils

BBCLASSEXTEND = "native nativesdk"

do_install_append() {
   # Cleanup unused item...
   rmdir ${D}${datadir}/share

   # We don't support the following items
   rm -rf ${D}${libdir}/python*/site-packages/smart/backends/slack
   rm -rf ${D}${libdir}/python*/site-packages/smart/backends/arch
   rm -rf ${D}${libdir}/python*/site-packages/smart/interfaces/qt

   # Temporary, debian support in OE is missing the python module
   rm -rf ${D}${libdir}/python*/site-packages/smart/backends/deb

   if [ -z "${@base_contains('PACKAGECONFIG', 'rpm', 'rpm', '', d)}" ]; then
      rm -rf ${D}${libdir}/python*/site-packages/smart/backends/rpm
   fi

   if [ -z "${@base_contains('PACKAGECONFIG', 'qt4', 'qt4', '', d)}" ]; then
      rm -rf ${D}${libdir}/python*/site-packages/smart/interfaces/qt4
   fi

   if [ -z "${@base_contains('PACKAGECONFIG', 'gtk+', 'gtk', '', d)}" ]; then
      rm -rf ${D}${libdir}/python*/site-packages/smart/interfaces/gtk
   fi
}

PACKAGES  = "python-smartpm-dev python-smartpm-dbg python-smartpm-doc smartpm"
PACKAGES += "${@base_contains('PACKAGECONFIG', 'rpm', 'python-smartpm-backend-rpm', '', d)}"
PACKAGES += "${@base_contains('PACKAGECONFIG', 'qt4', 'python-smartpm-interface-qt4', '', d)}"
PACKAGES += "${@base_contains('PACKAGECONFIG', 'gtk', 'python-smartpm-interface-gtk', '', d)}"
PACKAGES += "python-smartpm-interface-images"
PACKAGES += "python-smartpm"

RDEPENDS_smartpm = 'python-smartpm'

RDEPENDS_python-smartpm_append = " virtual/python-smartpm-backend python-codecs python-textutils python-xml"
RDEPENDS_python-smartpm_append += " python-fcntl python-pickle python-crypt python-compression python-shell"
RDEPENDS_python-smartpm_append += " python-resource python-netclient python-threading python-unixadmin"

#RDEPENDS_python-smartpm_append += " python-modules"

RDEPENDS_python-smartpm-backend-rpm = 'python-rpm'
RPROVIDES_python-smartpm-backend-rpm = 'virtual/python-smartpm-backend'

RDEPENDS_python-smartpm-interface-qt4 = 'qt4-x11 python-smartpm-interface-images'
RDEPENDS_python-smartpm-interface-gtk = 'gtk+ python-smartpm-interface-images'

FILES_smartpm = "${bindir}/smart"

FILES_${PN}-dbg += "${libdir}/python*/site-packages/smart/backends/rpm/.debug"

FILES_python-smartpm-backend-rpm = "${libdir}/python*/site-packages/smart/backends/rpm"

FILES_python-smartpm-interface-qt4 = "${libdir}/python*/site-packages/smart/interfaces/qt4"
FILES_python-smartpm-interface-gtk = "${libdir}/python*/site-packages/smart/interfaces/gtk"
FILES_python-smartpm-interface-images = "${datadir}/${baselib}/python*/site-packages/smart/interfaces/images"
