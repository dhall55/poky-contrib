SUMMARY = "Provide a basic init script to enable audio on snb, derived from n450-audio"
DESCRIPTION = "Set the volume and unmute the Front mixer setting during boot."
SECTION = "base"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${POKYBASE}/LICENSE;md5=3f40d7994397109285ec7b81fdeb3b58"

PR = "r0"

inherit update-rc.d

RDEPENDS = "alsa-utils-amixer"

SRC_URI = "file://snb-audio"

INITSCRIPT_NAME = "snb-audio"
INITSCRIPT_PARAMS = "defaults 90"

do_install() {
	install -d ${D}${sysconfdir} \
	           ${D}${sysconfdir}/init.d
	install -m 0755 ${WORKDIR}/snb-audio ${D}${sysconfdir}/init.d
        cat ${WORKDIR}/${INITSCRIPT_NAME} | \
            sed -e 's,/etc,${sysconfdir},g' \
                -e 's,/usr/sbin,${sbindir},g' \
                -e 's,/var,${localstatedir},g' \
                -e 's,/usr/bin,${bindir},g' \
                -e 's,/usr,${prefix},g' > ${D}${sysconfdir}/init.d/${INITSCRIPT_NAME}
        chmod 755 ${D}${sysconfdir}/init.d/${INITSCRIPT_NAME}
}

