DESCRIPTION = "WebKitGTK+ is the port of the portable web rendering engine WebKitK to the GTK+ platform."
HOMEPAGE = "http://www.webkitgtk.org/"
BUGTRACKER = "http://bugs.webkit.org/"

LICENSE = "BSD & LGPLv2+"

SRCREV = "101488"
PV = "1.7.2+svnr${SRCPV}"
PR = "r6"

SRC_URI = "\
  svn://svn.webkit.org/repository/webkit/trunk/;module=configure.ac;proto=http;singlefile=1 \
 "

S = "${WORKDIR}/"
