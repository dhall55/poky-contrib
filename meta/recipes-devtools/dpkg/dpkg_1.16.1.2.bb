require dpkg.inc
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe"

SRC_URI += "file://noman.patch \
            file://check_snprintf.patch \
            file://check_version.patch \
            file://perllibdir.patch \
            file://preinst.patch \
	    file://hijack-buildarch.patch"

SRC_URI[md5sum] = "068ae5e650e54968230de19d6c4e2241"
SRC_URI[sha256sum] = "d0ae363f41c4f1c23091afd9517d41de0f46b5ce7ecdda12dc4fbafa6dd55138"

PR = "${INC_PR}.0"

do_configure_prepend () {
    sed -i -e "s:##BUILDARCH##:${TARGET_ARCH}:g" ${S}/scripts/Dpkg/Arch.pm
}

