DEPENDS = "virtual/${TARGET_PREFIX}binutils ${NATIVEDEPS}"
DEPENDS += "virtual/${TARGET_PREFIX}libc-initial gettext-native"
PROVIDES = "virtual/${TARGET_PREFIX}gcc-intermediate"
PACKAGES = ""

CROSS_TARGET_SYS_DIR_append = ".${PN}"

# This is intended to be a -very- basic config
# sysroot is needed in case we use libc-initial
EXTRA_OECONF = "--with-local-prefix=${STAGING_DIR_TARGET}${target_prefix} \
		--enable-shared \
		--disable-multilib \
		--disable-threads \
		--enable-languages=c \
                ${OPTSPACE} \
		--program-prefix=${TARGET_PREFIX} \
		--with-sysroot=${STAGING_DIR_TCBOOTSTRAP} \
		--with-build-sysroot=${STAGING_DIR_TCBOOTSTRAP} \
		${EXTRA_OECONF_INTERMEDIATE} \
		${@get_gcc_fpu_setting(bb, d)}"

do_populate_sysroot[sstate-inputdirs] = "${SYSROOT_DESTDIR}/${STAGING_DIR_HOST} ${SYSROOT_DESTDIR}/${STAGING_DIR_TARGET}/${target_base_libdir}"
do_populate_sysroot[sstate-outputdirs] = "${STAGING_DIR_HOST} ${STAGING_DIR_TCBOOTSTRAP}/${target_base_libdir}"

do_compile () {
    oe_runmake
}

do_install () {
	oe_runmake 'DESTDIR=${D}' install
	install -d ${D}${target_base_libdir}/
	install -d ${D}${target_libdir}/
	mv ${D}${exec_prefix}/${TARGET_SYS}/lib/* ${D}${target_base_libdir}/
	rm -f ${D}${target_base_libdir}/libgcc_s.so
	rm -f ${D}${target_libdir}/libgcc_s.so
	echo "/* GNU ld script
   Use the shared library, but some functions are only in
   the static library.  */
GROUP ( libgcc_s.so.1 libgcc.a )" > ${D}${target_libdir}/libgcc_s.so

}

