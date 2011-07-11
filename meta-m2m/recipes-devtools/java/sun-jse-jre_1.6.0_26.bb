SUMMARY = "Sun Java SE JRE Update 26 binaries"
DESCRIPTION = "This is the proprietary JRE from Sun, with the Hotspot JVM.  In order to install it, we can't use an automated process - the user needs to manually agree to two separate license click-throughs, one in order to download the installer, the other when running the installer.  For this particular recipe, you need to download 'Linux x86 - Self Extracting Installer (jdk-6u26-linux-i586.bin)' (or x64, etc) from http://www.oracle.com/technetwork/java/javase/downloads/index.html.  Execute 'sh jre-6u26-linux-i586.bin' which will extract the contents into a jre1.6.0_26 directory.  Execute 'cp -a jre1.6.0_26 /path/to/yocto/meta-m2m/recipes-devtools/java/sun-jse-jre'.  At this point, the recipe will be ready to use in an image that includes it e.g. core-image-m2m-jre-live"

LICENSE = "Oracle Binary Code License Agreement"
LIC_FILES_CHKSUM = "file://${WORKDIR}/jre${PV}_${PV2}/LICENSE;md5=98f46ab6481d87c4d77e0e91a6dbc15f \
                    file://${WORKDIR}/jre${PV}_${PV2}/COPYRIGHT;md5=634ae2f49472680ca62359b8f4ec8c26"
PR = "r0"

# ok, this is a bogus hack, but works for now.  The name of
# the 'source' file is jre1.6.0_26, so we want to use PV to
# refer to the source, but the underscore prevents it.  We
# use the 2 underscores in the recipe name and hack the last
# bit back on.
PV2 = "26"

FILESPATH = "${FILE_DIRNAME}/sun-jse-jre"

FILES_${PN} = "/usr/*"

SRC_URI = "file://jre${PV}_${PV2}"

S = "${WORKDIR}"

do_install () {
	install -d -m 0755			${D}/usr/jre${PV}_${PV2}
	cp -a ${S}/jre${PV}_${PV2}		${D}/usr/
	ln -sf jre${PV}_${PV2}			${D}/usr/java
}

# The below is needed to avoid:
# | OSError: [Errno 40] Too many levels of symbolic links: ...
# see README

INHIBIT_PACKAGE_DEBUG_SPLIT = "1"