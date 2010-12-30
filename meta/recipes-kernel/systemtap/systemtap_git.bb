DESCRIPTION = "SystemTap"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=94d55d512a9ba36caa9b7df079bae19f"

DEPENDS = "elfutils rpm"

PR = r0
PV = "1.3+git${SRCPV}"

#PV = "release-1.3+git${SRCPV}"

SRC_URI = "git://sources.redhat.com/git/systemtap.git;protocol=git \
          "

EXTRA_OECONF = "--prefix=${D} --with-libelf=${STAGING_DIR_TARGET} --without-rpm \
	     ac_cv_file__usr_include_nss=no \
	     ac_cv_file__usr_include_nss3=no \
	     ac_cv_file__usr_include_nspr=no \
	     ac_cv_file__usr_include_nspr4=no \
	     ac_cv_file__usr_include_avahi_client=no \
	     ac_cv_file__usr_include_avahi_common=no "

CXXFLAGS += " -I${STAGING_INCDIR}/rpm"

#SRC_URI[md5sum]    = "80902a7b3d6f7cb83eb6b47e87538747"
#SRC_URI[sha256sum] = "1c6403278fa4f3b37a1fb9f0784e496dce1703fe84ac03b2650bf469133a0cb3"

S = "${WORKDIR}/git"

inherit autotools
