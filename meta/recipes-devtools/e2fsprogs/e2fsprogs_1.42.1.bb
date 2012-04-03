require e2fsprogs.inc

PR = "r0"

SRC_URI += "file://fallocate.patch \
            file://acinclude.m4 \
            file://remove.ldconfig.call.patch \
"

SRC_URI[md5sum] = "8ed1501ae6746e2e735bdd1407211dc9"
SRC_URI[sha256sum] = "0f1fdc10c6289b6750714490837df9aab691f352d33f5ecb64507704df6ff991"

EXTRA_OECONF += "--libdir=${base_libdir} --sbindir=${base_sbindir} --enable-elf-shlibs --disable-libuuid --disable-uuidd"
EXTRA_OECONF_darwin = "--libdir=${base_libdir} --sbindir=${base_sbindir} --enable-bsd-shlibs"
EXTRA_OECONF_darwin8 = "--libdir=${base_libdir} --sbindir=${base_sbindir} --enable-bsd-shlibs"

do_configure_prepend () {
	cp ${WORKDIR}/acinclude.m4 ${S}/
}

do_compile_prepend () {
	find ./ -print | grep -v ./patches | xargs chmod u=rwX
	( cd util; ${BUILD_CC} subst.c -o subst )
}

do_install () {
	oe_runmake 'DESTDIR=${D}' install
	oe_runmake 'DESTDIR=${D}' install-libs
	# We use blkid from util-linux now so remove from here
	rm -f ${D}${base_libdir}/libblkid*
	rm -rf ${D}${includedir}/blkid
	rm -f ${D}${base_libdir}/pkgconfig/blkid.pc
}

do_install_append () {
	# e2initrd_helper and the pkgconfig files belong in libdir
	if [ ! ${D}${libdir} -ef ${D}${base_libdir} ]; then
		install -d ${D}${libdir}
		mv ${D}${base_libdir}/e2initrd_helper ${D}${libdir}
		mv ${D}${base_libdir}/pkgconfig ${D}${libdir}
	fi
}

# blkid used to be part of e2fsprogs but is useful outside, add it
# as an RDEPENDS_${PN} so that anything relying on it being in e2fsprogs
# still works
RDEPENDS_e2fsprogs = "e2fsprogs-blkid e2fsprogs-badblocks"

PKGSUFFIX = ""

PACKAGES =+ "e2fsprogs-blkid${PKGSUFFIX} e2fsprogs-e2fsck${PKGSUFFIX} e2fsprogs-mke2fs${PKGSUFFIX} e2fsprogs-fsck${PKGSUFFIX} e2fsprogs-tune2fs${PKGSUFFIX} e2fsprogs-badblocks${PKGSUFFIX}"
PACKAGES =+ "libcomerr${PKGSUFFIX} libss${PKGSUFFIX} libe2p${PKGSUFFIX} libext2fs${PKGSUFFIX}"

FILES_e2fsprogs-blkid${PKGSUFFIX} = "${base_sbindir}/blkid"
FILES_e2fsprogs-fsck${PKGSUFFIX} = "${base_sbindir}/fsck"
FILES_e2fsprogs-e2fsck${PKGSUFFIX} = "${base_sbindir}/e2fsck ${base_sbindir}/fsck.ext*"
FILES_e2fsprogs-mke2fs${PKGSUFFIX} = "${base_sbindir}/mke2fs ${base_sbindir}/mkfs.ext* ${sysconfdir}/mke2fs.conf"
FILES_e2fsprogs-tune2fs${PKGSUFFIX} = "${base_sbindir}/tune2fs ${base_sbindir}/e2label ${base_sbindir}/findfs"
FILES_e2fsprogs-badblocks${PKGSUFFIX} = "${base_sbindir}/badblocks"
FILES_libcomerr${PKGSUFFIX} = "${base_libdir}/libcom_err.so.*"
FILES_libss${PKGSUFFIX} = "${base_libdir}/libss.so.*"
FILES_libe2p${PKGSUFFIX} = "${base_libdir}/libe2p.so.*"
FILES_libext2fs${PKGSUFFIX} = "${libdir}/e2initrd_helper ${libdir}/libext2fs.so.*"
FILES_${PN}-dev${PKGSUFFIX} += "${datadir}/*/*.awk ${datadir}/*/*.sed ${base_libdir}/*.so"

BBCLASSEXTEND = "native nativesdk"
