python siteconfig_do_siteconfig () {
	shared_state = sstate_state_fromvars(d)
	if shared_state['name'] != 'populate-sysroot':
		return
	if not os.path.isdir(os.path.join(bb.data.getVar('FILE_DIRNAME', d, 1), 'site_config')):
		bb.debug(1, "No site_config directory, skipping do_siteconfig")
		return
	bb.build.exec_func('do_siteconfig_gencache', d)
	sstate_clean(shared_state, d)
	sstate_install(shared_state, d)
}

siteconfig_do_siteconfig_gencache () {
	mkdir ${WORKDIR}/site_config
	gen-site-config ${FILE_DIRNAME}/site_config \
		>${WORKDIR}/site_config/configure.ac
	cd ${WORKDIR}/site_config
	autoconf
        CONFIG_SITE="" ./configure ${CONFIGUREOPTS} --cache-file ${PN}_cache
	sed -n -e "/ac_cv_c_bigendian/p" -e "/ac_cv_sizeof_/p" \
		-e "/ac_cv_type_/p" -e "/ac_cv_header_/p" -e "/ac_cv_func_/p" \
		< ${PN}_cache > ${PN}_config
	mkdir -p ${SYSROOT_DESTDIR}${SITECONFIG_SYSROOTCACHE}
	cp ${PN}_config ${SYSROOT_DESTDIR}${SITECONFIG_SYSROOTCACHE}
}

do_populate_sysroot[sstate-interceptfuncs] += "do_siteconfig "

EXPORT_FUNCTIONS do_siteconfig do_siteconfig_gencache
