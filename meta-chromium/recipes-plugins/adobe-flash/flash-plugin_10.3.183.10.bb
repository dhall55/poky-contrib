DESCRIPTION = "Adobe Flash player plugin for web browsers"

LICENSE = "AdobeFlash"
LIC_FILES_CHKSUM = "file://../libflashplayer.so;md5=eeecff9f98b725a00fba114ce1f46621"

# Uncommenting the below line means you accept the Adobe Flash license!
#LIC_FILES_CHKSUM += "file://You_must_accept_the_Adobe_Flash_license;md5sum=0000000000000000"

PR = "r0"

RDEPENDS = "libcurl5 nspr nss procps"

SRC_URI = "${ADOBE_MIRROR}/install_flash_player_10_linux.tar.gz"

SRC_URI[md5sum] = "f04482fcfa0ccd081447d15341762978"
SRC_URI[sha256sum] = "dfd5bbf4689465cc56b0a883b8368a1c13be6bdd0d594fc81a0129055e0b453a"

INHIBIT_PACKAGE_STRIP = "1"

do_install() {
    install -d ${D}${libdir}/mozilla/plugins/
    install -m 0755 ${WORKDIR}/libflashplayer.so ${D}${libdir}/mozilla/plugins/
}

FILES_${PN} = "${libdir}/*"
