DESCRIPTION = "gnu-configize"
SECTION = "devel"
LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://config.guess;beginline=9;endline=39;md5=b41f5a207cf8503d8706f4cf0844cd47"
DEPENDS = ""
INHIBIT_DEFAULT_DEPS = "1"

SRCREV = "3155524d0410c37b6286465249264c7981ab8cba"
SRCREV_SHORT = "${@bb.data.getVar('SRCREV', d, 1)[0:7]}"

PV = "0.0+git${SRCREV_SHORT}"
PR = "r0"

# Bellow is the git web interface pointer to the tarball. The ';' in the url  
# currently is not working for the bitbake http fetcher. Until that bug gets 
# fixed using the autobuilder source mirror url to get the tarball.
#
# SRC_URI="http://git.savannah.gnu.org/gitweb/?p=config.git;a=snapshot;h=${SRCREV};sf=tgz;localfile=${DL_DIR}/config-${SRCREV_SHORT}.tar.gz "

SRC_URI = "\
        http://autobuilder.pokylinux.org/sources/config-${SRCREV_SHORT}.tar.gz \
	file://config-guess-uclibc.patch \
        file://gnu-configize.in"

S = "${WORKDIR}/config-${SRCREV_SHORT}/"

do_compile() {
	:
}

do_install () {
	install -d ${D}${datadir}/gnu-config \
		   ${D}${bindir}
	cat ${WORKDIR}/gnu-configize.in | \
		sed -e 's,@gnu-configdir@,${datadir}/gnu-config,g' \
		    -e 's,@autom4te_perllibdir@,${datadir}/autoconf,g' > ${D}${bindir}/gnu-configize
	# In the native case we want the system perl as perl-native can't have built yet
	if [ "${BUILD_ARCH}" != "${TARGET_ARCH}" ]; then
		sed -i -e 's,/usr/bin/perl,${bindir}/perl,g' ${D}${bindir}/gnu-configize
	fi
	chmod 755 ${D}${bindir}/gnu-configize
	install -m 0644 config.guess config.sub ${D}${datadir}/gnu-config/
}

PACKAGES = "${PN}"
FILES_${PN} = "${bindir} ${datadir}/gnu-config"

BBCLASSEXTEND = "native"
