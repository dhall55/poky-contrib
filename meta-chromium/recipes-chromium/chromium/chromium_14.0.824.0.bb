DESCRIPTION = "Google Chrome browser"
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSE;md5=3cb55cc4ec38bb01d2ceaaa66b5436c2"

DEPENDS = "xextproto cairo nss cups libxscrnsaver"

RDEPENDS = "nspr nss flash-plugin ttf-wqy-zenhei ttf-arphic-uming alsa-utils"

PR = "r0"

# The size of chromium.r92735.tgz is about 1.15G bytes, so we would take
# some time to download it...
SRC_URI = "http://chromium-browser-source.commondatastorage.googleapis.com/chromium.r92735.tgz \
           git://git.chromium.org/git/cros.git;protocol=http;rev=07f1fc0ce7a4bbd57f6b057435ad86f0a98e073d\
           http://src.chromium.org/svn/trunk/tools/depot_tools.tar.gz;name=depot \
           file://gypi.patch \
           file://include.gypi \
           file://chrome.desktop \
          "

SRC_URI[depot.md5sum] = "f9148f0744194b1988a5a62abe77b5c4"
SRC_URI[depot.sha256sum] = "4a6f6a9d7c5489f7009b7bf723905231411b9cf67b0567e11b575a2d73f69079"

S = "${WORKDIR}/src"

inherit gettext

do_fixup_code_path() {
    cd ${WORKDIR}
    mv home/chrome-svn/tarball/chromium/src ./
}

addtask fixup_code_path after do_unpack before do_patch

do_configure() {
    cd ${WORKDIR}
    export GYP_GENERATORS=make
    export PATH=${WORKDIR}/depot_tools:"$PATH"

    rm -f ${S}/tools/gyp/pylib/gyp/__init__.pyc
    rm -f ${S}/tools/gyp/pylib/gyp/__init__.pyo
    sed -e 's|__PATH__TO_BE_REPLACED__|"${WORKDIR}/include.gypi"|' -i ${S}/tools/gyp/pylib/gyp/__init__.py
    sed -e "s|__PATH__TO_BE_REPLACED__|${STAGING_DIR_TARGET}|" -i ${WORKDIR}/include.gypi

    if [ ! -e ${WORKDIR}/.gclient ] ; then
        gclient config http://src.chromium.org/svn/trunk/src
    fi

    # This is the command lines to download everything but it's done in do_fetch_post
    #depot_tools/gclient sync --revision src@${SRCREV} --force --verbose
    gclient runhooks --force
}

TARGET_CC_ARCH += "${LDFLAGS}"

do_compile() {
    cd ${S}
    export CROSSTOOL=${STAGING_BINDIR_TOOLCHAIN}/${TARGET_PREFIX}
    export AR=${CROSSTOOL}ar
    export AS=${CROSSTOOL}as
    export LD=${CROSSTOOL}ld
    export RANLIB=${CROSSTOOL}ranlib
    oe_runmake -r ${PARALLEL_MAKE} V=1 BUILDTYPE=Release chrome
}

do_install() {
    install -d ${D}${bindir}
    install -d ${D}${bindir}/chrome/
    install -m 0755 ${S}/out/Release/chrome ${D}${bindir}/chrome/
    install -m 0644 ${S}/out/Release/chrome.pak ${D}${bindir}/chrome/
    install -m 0644 ${S}/out/Release/resources.pak ${D}${bindir}/chrome/
    install -m 0644 ${S}/out/Release/product_logo_48.png ${D}${bindir}/chrome/

    install -d ${D}${bindir}/chrome/plugins/
    ln -s /usr/java/jre/lib/i386/libnpjp2.so ${D}${bindir}/chrome/plugins/

    ln -s /usr/bin/chrome/chrome ${D}${bindir}/chromium

    install -d ${D}${bindir}/chrome/locales/
    install -m 0644 ${S}/out/Release/locales/en-US.pak ${D}${bindir}/chrome/locales
    cp -a ${S}/out/Release/obj ${D}${bindir}/chrome/
    cp -a ${S}/out/Release/obj.target ${D}${bindir}/chrome/
    cp -a ${S}/out/Release/resources ${D}${bindir}/chrome/

    install -d ${D}${datadir}/applications/
    install -m 0644 ${WORKDIR}/chrome.desktop ${D}${datadir}/applications/

    find ${D}${bindir}/chrome/ -name "*.d" -delete
    find ${D}${bindir}/chrome/ -name "*.o" -delete
    find ${D}${bindir}/chrome/ -name "*.a" -delete
    find ${D}${bindir}/chrome/ -name "*.cpp" -delete
    find ${D}${bindir}/chrome/ -name "*.h" -delete
    find ${D}${bindir}/chrome/ -name "*.cc" -delete
}

FILES_${PN} = "${bindir}/chrome/ ${bindir}/chromium ${datadir}/applications/chrome.desktop"
FILES_${PN}-dbg = "${bindir}/chrome/.debug/ ${exec_prefix}/src/debug/"
