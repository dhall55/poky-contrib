require recipes-devtools/gcc/gcc-4.5.1.inc

FILESPATH = "${FILE_DIRNAME}/gcc-${PV}/:${FILE_DIRNAME}/gcc-4.5.1/"
FILESDIR = "${WORKDIR}"

SRC_URI = "http://launchpad.net/gcc-linaro/4.5/4.5-2010.11-0/+download/gcc-linaro-4.5-2010.11-1.tar.bz2 \
	   file://change_base_version_to_4.5.1.linaro.patch \
	   file://gcc-4.3.1-ARCH_FLAGS_FOR_TARGET.patch \
	   file://100-uclibc-conf.patch \
           file://gcc-uclibc-locale-ctype_touplow_t.patch \
	   file://cache-amnesia.patch \
	   file://gcc-flags-for-build.patch \
	   file://libstdc++-emit-__cxa_end_cleanup-in-text.patch \
	   file://arm-bswapsi2.patch \
		\
           file://fedora/gcc43-c++-builtin-redecl.patch;striplevel=0 \
           file://fedora/gcc43-ia64-libunwind.patch;striplevel=0 \
           file://fedora/gcc43-java-nomulti.patch;striplevel=0 \
           file://fedora/gcc43-ppc32-retaddr.patch;striplevel=0 \
           file://fedora/gcc43-pr32139.patch;striplevel=0 \
           file://fedora/gcc43-pr33763.patch;striplevel=0 \
           file://fedora/gcc43-rh330771.patch;striplevel=0 \
           file://fedora/gcc43-rh341221.patch;striplevel=0 \
           file://fedora/gcc43-java-debug-iface-type.patch;striplevel=0 \
           file://fedora/gcc43-i386-libgomp.patch;striplevel=0 \
           file://103-uclibc-conf-noupstream.patch  \
           file://200-uclibc-locale.patch  \
           file://203-uclibc-locale-no__x.patch;striplevel=1 \
           file://204-uclibc-locale-wchar_fix.patch;striplevel=1 \
           file://205-uclibc-locale-update.patch;striplevel=1 \
           file://301-missing-execinfo_h.patch  \
           file://302-c99-snprintf.patch  \
           file://303-c99-complex-ugly-hack.patch  \
           file://304-index_macro.patch  \
           file://305-libmudflap-susv3-legacy.patch  \
           file://306-libstdc++-namespace.patch  \
           file://740-sh-pr24836.patch  \
           file://800-arm-bigendian.patch  \
           file://904-flatten-switch-stmt-00.patch  \
           file://arm-nolibfloat.patch  \
           file://arm-softfloat.patch \
           file://zecke-xgcc-cpp.patch \
           file://gcc-poison-system-directories.patch \
           file://gcc-poison-dir-extend.patch \
           file://gcc-4.3.3-SYSROOT_CFLAGS_FOR_TARGET.patch \
	   file://64bithack.patch \
	   file://optional_libstdc.patch \
	   file://disable_relax_pic_calls_flag.patch \
	   file://gcc-poison-parameters.patch \
	  "

do_move_src() {
	echo moving ${WORKDIR}/gcc-linaro-4.5-2010.11-1 ${WORKDIR}/gcc-${PV}
	mv ${WORKDIR}/gcc-linaro-4.5-2010.11-1 ${WORKDIR}/gcc-${PV}
}

do_unpack_append() {
	bb.build.exec_func('do_move_src', d)
}
