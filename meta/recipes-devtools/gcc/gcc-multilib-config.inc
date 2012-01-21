addtask gcc_multilib_setup after do_patch before do_configure

do_gcc_multilib_setup() {
	set -x
	# do this only for target recipe
	if [ "${PN}" !=  "gcc" ]
	then
		return
	fi

	if [ "${MULTILIBS}" == "" ]
	then
		# nothing to do
		return
	fi

	for ml in `echo ${MULTILIBS} | sed -e "s+multilib:++g"`
	do
		echo ml=$ml 
		ml_tune="${DEFAULTTUNE_virtclass-multilib-${ml}}"
		ml_tune_features="${TUNE_FEATURES_tune-${ml_tune}}"
		ml_baselib="${BASE_LIB_tune-${ml_tune}}"
		echo ml_tune=$ml_tune 
		echo ml_tune_features=$ml_tune_features
		echo ml_baselib=$ml_baselib
		ml_tune_ccargs = ""
		for feature in ${ml_tune_features}
		do
			echo feature=$feature
			ml_feature_ccargs = "${TUNE_CCARGS_${feature}}"
			echo ml_feature_ccargs=$ml_feature_ccargs
			ml_tune_ccargs += "${ml_feature_ccargs}"
		done
		echo ml_tune_ccargs=$ml_tune_ccargs
	done
}
