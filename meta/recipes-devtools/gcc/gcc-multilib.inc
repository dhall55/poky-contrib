addtask gcc_multilib_setup after do_patch before do_configure


do_gcc_multilib_setup() {
	# do this only for target recipe
	if ${PN} != "gcc" :
		return

	if "${MULTILIBS}" == "" :
		# nothing to do
		return

	multilibs = string_substitute(MULTILIBS, "multilib:", "")

	for ml in multilibs:
		ml_tune = "${DEFAULTTUNE_virtclass-multilib-${ml}}"
		ml_tune_features = "${TUNE_FEATURES_tune-${ml_tune}}"
		ml_baselib = "${BASE_LIB_tune-${ml_tune}}"
		ml_tune_ccargs = ""
		for feature in ml_tune_features:
			ml_feature_ccargs = "${TUNE_CCARGS_${feature}}"
			ml_tune_ccargs += "${ml_feature_ccargs}"
	

}
