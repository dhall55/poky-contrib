require gcc-${PV}.inc

INHIBIT_DEFAULT_DEPS = "1"
DEPENDS = "virtual/${TARGET_PREFIX}gcc virtual/${TARGET_PREFIX}g++"

PACKAGES = "\
  ${PN} \
  ${PN}-dev \
  ${PN}-dbg \
  libgcov-dev \
  "

FILES_${PN} = "${base_libdir}/libgcc*.so.*"
FILES_${PN}-dev = " \
  ${base_libdir}/libgcc*.so \
  ${libdir}/${TARGET_SYS}/${BINV}/crt* \
  ${libdir}/${TARGET_SYS}/${BINV}/32 \
  ${libdir}/${TARGET_SYS}/${BINV}/x32 \
  ${libdir}/${TARGET_SYS}/${BINV}/n32 \
  ${libdir}/${TARGET_SYS}/${BINV}/libgcc*"
FILES_libgcov-dev = " \
  ${libdir}/${TARGET_SYS}/${BINV}/libgcov.a "

FILES_${PN}-dbg += "${base_libdir}/.debug/"

do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install () {
	target=`echo ${MULTIMACH_TARGET_SYS} | sed -e s#-nativesdk##`

	# Install libgcc from our gcc-cross saved data
	install -d ${D}${base_libdir} ${D}${libdir}
	cp -fpPR ${STAGING_INCDIR_NATIVE}/gcc-build-internal-$target/* ${D}

	# Move libgcc_s into /lib
	mkdir -p ${D}${base_libdir}
	if [ -f ${D}${libdir}/nof/libgcc_s.so ]; then
		mv ${D}${libdir}/nof/libgcc* ${D}${base_libdir}
	else
		mv ${D}${libdir}/libgcc* ${D}${base_libdir} || true
	fi

	chown -R root:root ${D}
	chmod +x ${D}${base_libdir}/libgcc_s.so.*
}

do_package_write_ipk[depends] += "virtual/${MLPREFIX}libc:do_package"
do_package_write_deb[depends] += "virtual/${MLPREFIX}libc:do_package"
do_package_write_rpm[depends] += "virtual/${MLPREFIX}libc:do_package"

BBCLASSEXTEND = "nativesdk"

INSANE_SKIP_libgcc-dev = "staticdev"
INSANE_SKIP_libgcov-dev = "staticdev"

addtask multilib_install after do_install before do_package


# this makes multilib gcc files findable for target gcc
# like this directory is made findable 
#    /usr/lib/i586-pokymllib32-linux/4.6.3/
# by creating this symlink to it
#    /usr/lib64/x86_64-poky-linux/4.6.3/32

python do_multilib_install() {
        import re
        # do this only for multilib extended recipe
        if d.getVar('PN', 1) != 'libgcc':
                return

        tune_arch = d.getVar('TUNE_ARCH', 1) or ''
        defaulttune = d.getVar('DEFAULTTUNE', 1) or ''
        multilibs = d.getVar('MULTILIB_VARIANTS', 1) or ''
        if multilibs == '':
                return

	tunes_32 = ['x86', 'core2', 'i586', 'mips', 'mipsel', 'mips-nf', 'mipsel-nf', 'powerpc', 'powerpc-nf']
        tunes_64 = ['x86-64', 'core2-64', 'mips64', 'mips64el', 'mips64-nf', 'mips64el-nf', 'powerpc64']
        tunes_x32 = ['x86-64-x32', 'core2-64-x32']
        tunes_n32 = ['mips64-n32', 'mips64el-n32', 'mips64-nf-n32', 'mips64el-nf-n32']

        for ml in multilibs.split(' '):
                ml_tune = d.getVar('DEFAULTTUNE_virtclass-multilib-' + ml, 1) or ''
		ml_tune_features = d.getVar('TUNE_FEATURES_tune-' + ml_tune, 1) or ''
                ml_baselib = d.getVar('BASE_LIB_tune-' + ml_tune, 1) or ''
                for feature in ml_tune_features.split():
                        ml_feature_arch = d.getVar('TUNE_FEATURE_ARCH-' + feature, 1) or ''
		if ml_tune in tunes_32:
                        bitness = '32'
                elif ml_tune in tunes_64:
                        bitness = '64'
                elif ml_tune in tunes_x32:
                        bitness = 'x32'
                elif ml_tune in tunes_n32:
                        bitness = 'n32'

	binv = d.getVar('BINV', 1) or ''

	src = '/usr/' + ml_baselib + '/' + ml_feature_arch + '-pokyml' + ml + '-linux/' + binv + '/' 
	dest = (d.getVar('D', 1) or '') + (d.getVar('libdir', 1) or '') + '/' + (d.getVar('TARGET_SYS', 1) or '') + '/' + binv + '/' + bitness
	if os.path.lexists(dest):
		os.unlink(dest)
	os.symlink(src, dest)

}
