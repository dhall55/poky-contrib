TUNEVALID += "callconvention-hard"
TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "callconvention-hard", "-mfloat-abi=hardfp", "-mfloat-abi=softfp" ,d)}"
ARMSFX .= "${@bb.utils.contains("TUNE_FEATURES", "callconvention-hard", "-hfp", "" ,d)}"

