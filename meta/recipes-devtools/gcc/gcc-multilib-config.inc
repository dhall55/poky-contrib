addtask gcc_multilib_setup after do_patch before do_configure

python do_gcc_multilib_setup() {
	# do this only for target recipe
 	if d.getVar('PN', 1) != "gcc":
		return

 	multilibs = d.getVar('MULTILIBS', 1) or ""
 	if multilibs == "":
		return
	bb.warn(multilibs)

	gcc_target_config_files = { 	"x86_64"	: "gcc/config/i386/t-linux64",
					"mips"		: "gcc/config/mips/t-linux64" ,
					"ppc" 		: "gcc/config/rs6000/t-linux64" }

 	target_arch = d.getVar('TARGET_ARCH', 1) or ""
	bb.warn(target_arch)

	gcc_multilib_config_file = gcc_target_config_files[target_arch]
	bb.warn(gcc_multilib_config_file)

	multilib_options = []
	multilib_dirnames = []
	multilib_osdirnames = []

	for ml in multilibs.replace("multilib:", "").split():
		bb.warn(ml)
 		ml_tune = d.getVar('DEFAULTTUNE_virtclass-multilib-' + ml, 1) or ""
		bb.warn(ml_tune)
 		ml_tune_features = d.getVar('TUNE_FEATURES_tune-' + ml_tune, 1) or ""
		bb.warn(ml_tune_features)
 		ml_baselib = d.getVar('BASE_LIB_tune-' + ml_tune, 1) or ""
		bb.warn(ml_baselib)
		ml_tune_ccargs_list = []
		for feature in ml_tune_features.split():
			bb.warn(feature)
 			ml_feature_ccargs = d.getVar('TUNE_FEATURE_CCARGS-' + feature, 1) or ""
			bb.warn(ml_feature_ccargs)
			ml_tune_ccargs_list.append(ml_feature_ccargs)
		ml_tune_ccargs = ''.join(ml_tune_ccargs_list)
		multilib_options.append(ml_tune_ccargs)
		multilib_dirnames.append(ml_baselib.replace("lib", ""))
		multilib_osdirnames.append('../' + ml_baselib)
		bb.warn(ml_tune_ccargs)
}
