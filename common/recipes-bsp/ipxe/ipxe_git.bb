DESCRIPTION = "Open source network boot firmware"
HOMEPAGE = "http://ipxe.org"
LICENSE = "GPLv2"
DEPENDS = "binutils-native perl-native syslinux mtools-native"
LIC_FILES_CHKSUM = "file://../COPYING;md5=8ca43cbc842c2336e835926c2166c28b"

SRCREV = "bd9ff16c21efef27b6c18c15dc1d4b153ec12a4a"
PV = "1.0.0+gitr${SRCPV}"
PR = "r0"

inherit deploy

SRC_URI = "git://git.ipxe.org/ipxe.git;protocol=git \
	   file://chainload.ipxe"

EXTRA_OEMAKE = "NO_WERROR=1 EMBEDDED_IMAGE=../../chainload.ipxe"

S = "${WORKDIR}/git/src"

do_configure () {
	if [ -z "${IPXE_TFTP_HOST}" ] ; then
		echo "IPXE_TFTP_HOST not set, please set it in your local.conf."
		exit 1
	fi

	sed -i s#^ISOLINUX_BIN[\ \\t]*=.*#ISOLINUX_BIN\ =\ ${STAGING_DIR_TARGET}/usr/lib/syslinux/isolinux.bin# arch/i386/Makefile
	sed -i s/TFTP_HOST/${IPXE_TFTP_HOST}/g ../../chainload.ipxe
}

do_compile () {
        oe_runmake
}

do_deploy () {
        install ${S}/bin/ipxe.usb ${DEPLOYDIR}/
}
addtask deploy before do_build after do_compile

