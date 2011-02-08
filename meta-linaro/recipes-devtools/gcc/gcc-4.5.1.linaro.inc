require recipes-devtools/gcc/gcc-4.5.1.inc

FILESPATH = "${FILE_DIRNAME}/gcc-${PV}/:${FILE_DIRNAME}/gcc-4.5.1/"
FILESDIR = "${WORKDIR}"
DEPENDS =+ "mpfr gmp libmpc elfutils"
NATIVEDEPS = "mpfr-native gmp-native gettext-native libmpc-native elfutils-native"

LICENSE="GCC RUNTIME LIBRARY EXCEPTION & GPLv2 & GPLv3 & LGPLv2.1 & LGPLv3"

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552 \
                   file://COPYING3;md5=d32239bcb673463ab874e80d47fae504 \
                   file://COPYING3.LIB;md5=6a6a8e020838b23406c81b19c1d46df6 \
                   file://COPYING.LIB;md5=2d5025d4aa3495befef8f17206a5b0a1 \
		   file://COPYING.RUNTIME;md5=fe60d87048567d4fe8c8a0ed2448bcc8"

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
           file://fedora/gcc45-no-add-needed.patch;striplevel=0 \
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
	   file://GPLUSPLUS_INCLUDE_DIR_with_sysroot.patch \
	  "

SRC_URI[md5sum] = "9e18a60d2c5ae4f3338814aabf80bb90"
SRC_URI[sha256sum] = "34ba3938148c92c6d3622632a9a2408361af44d0ad3f37a76deac255679d4d0d"

do_move_src() {
	echo moving ${WORKDIR}/gcc-linaro-4.5-2010.11-1 ${WORKDIR}/gcc-${PV}
	mv ${WORKDIR}/gcc-linaro-4.5-2010.11-1 ${WORKDIR}/gcc-${PV}
}

do_unpack_append() {
	bb.build.exec_func('do_move_src', d)
}

# Language Overrides
FORTRAN = ""
JAVA = ""

#EXTRA_OECONF_BASE = "  --enable-cheaders=c_std \
#			--enable-libssp \
#			--disable-bootstrap \
#			--disable-libgomp \
#			--disable-libmudflap"
EXTRA_OECONF_BASE = " --enable-lto \
			--enable-libssp \
			--disable-bootstrap \
			--disable-libgomp \
			--disable-libmudflap \
			--enable-cheaders=c_global "

EXTRA_OECONF_INITIAL = "--disable-libmudflap \
			--disable-libgomp \
			--disable-libssp \
			--enable-decimal-float=no"

EXTRA_OECONF_INTERMEDIATE = "--disable-libmudflap \
				--disable-libgomp \
				--disable-libssp"

EXTRA_OECONF_append_linux-uclibc = " --disable-decimal-float "
EXTRA_OECONF_append_linux-uclibceabi = " --disable-decimal-float "
EXTRA_OECONF_append_linux-uclibcspe = " --disable-decimal-float "
