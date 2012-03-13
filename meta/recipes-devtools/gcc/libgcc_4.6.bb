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
  ${libdir}/${TARGET_SYS}/${BINV}/libgcov.a"

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
    if d.getVar('PN', True) != 'libgcc':
        return

    multilibs = d.getVar('MULTILIB_VARIANTS', True) or ''
    if multilibs == '':
        return

    binv = d.getVar('BINV', True) or ''

    for ml in multilibs.split(' '):
        tune = d.getVar('DEFAULTTUNE_virtclass-multilib-' + ml, True) or ''
        tune_parameters = get_tune_parameters(tune, d)
        tune_baselib = tune_parameters['baselib']
        tune_arch = tune_parameters['arch']
        tune_bitness = tune_baselib.replace('lib', '')
        if tune_bitness == '' :
            tune_bitness = '32' # /lib => 32bit lib

    src = d.getVar('target_prefix', True) + '/' + tune_baselib + '/' + \
        tune_arch + '-' + d.getVar('TARGET_VENDOR', True) + 'ml' + ml + \
        d.getVar('TARGET_OS', True) + '/' + binv + '/'

    dest = d.getVar('D', True) + d.getVar('libdir', True) + '/' + \
        d.getVar('TARGET_SYS', True) + '/' + binv + '/' + tune_bitness

    if os.path.lexists(dest):
        os.unlink(dest)
    os.symlink(src, dest)
}
