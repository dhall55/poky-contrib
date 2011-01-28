DESCRIPTION = "MediaTomb - UPnP AV MediaServer for Linux"
HOMEPAGE = "http://mediatomb.cc/"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=0b609ee7722218aa600220f779cb5035 \
                    file://src/main.cc;beginline=14;endline=25;md5=ba9c4cf20a63e18b1626c4c9d794635a"
DEPENDS = "expat ffmpeg sqlite3 libexif js zlib file id3lib ffmpegthumbnailer"
PR = "r2"

SRC_URI = "${SOURCEFORGE_MIRROR}/mediatomb/mediatomb-${PV}.tar.gz \
	   file://curl.diff \
	   file://inotify.diff \
	   file://init \
	   file://default \
	   file://config.xml \
	   "

inherit autotools pkgconfig update-rc.d

INITSCRIPT_NAME = "mediatomb"
INITSCRIPT_PARAMS = "defaults 90"

EXTRA_OECONF = "--disable-mysql \
		--disable-rpl-malloc \
		--enable-sqlite3 \
		--enable-libjs \
		--enable-libmagic \
		--enable-id3lib \
		--enable-libexif \
		--enable-db-autocreate \
		--disable-largefile \
		--with-sqlite3-h=${STAGING_INCDIR} \
		--with-sqlite3-libs=${STAGING_LIBDIR} \
		--with-magic-h=${STAGING_INCDIR} \
		--with-magic-libs=${STAGING_LIBDIR} \
		--with-exif-h=${STAGING_INCDIR} \
		--with-exif-libs=${STAGING_LIBDIR} \
		--with-zlib-h=${STAGING_INCDIR} \
		--with-zlib-libs=${STAGING_LIBDIR} \
		--with-js-h=${STAGING_INCDIR}/js \
		--with-js-libs=${STAGING_LIBDIR} \
		--with-id3lib-h=${STAGING_INCDIR} \
		--with-id3lib-libs=${STAGING_LIBDIR} \
		ac_cv_header_sys_inotify_h=yes"

SRC_URI[md5sum] = "661f08933830d920de21436fe122fb15"
SRC_URI[sha256sum] = "25e0b3d761e41fc6793c780eb7f638719867cdc6d3429ec24f72d1e9556ac1d2"

do_install() {
	autotools_do_install

	# install the daemonizing bits manually
	install -d ${D}${sysconfdir} \
		   ${D}${sysconfdir}/init.d \
		   ${D}${sysconfdir}/default \
		   ${D}${sysconfdir}/mediatomb \
		   ${D}${localstatedir}/lib/mediatomb
	
	cp ${WORKDIR}/default ${D}${sysconfdir}/default/mediatomb

	cat ${WORKDIR}/init | \
	    sed -e 's,/etc,${sysconfdir},g' \
		-e 's,/usr/sbin,${sbindir},g' \
		-e 's,/var,${localstatedir},g' \
		-e 's,/usr/bin,${bindir},g' \
		-e 's,/usr,${prefix},g' > ${D}${sysconfdir}/init.d/mediatomb
	chmod 755 ${D}${sysconfdir}/init.d/mediatomb

	cat ${WORKDIR}/config.xml | \
	    sed -e 's,/etc,${sysconfdir},g' \
		-e 's,/usr/sbin,${sbindir},g' \
		-e 's,/var,${localstatedir},g' \
		-e 's,/usr/bin,${bindir},g' \
		-e 's,/usr,${prefix},g' > ${D}${sysconfdir}/mediatomb/config.xml
}
