TUNEVALID += "bigendian"
TUNE_ARCH = "${@bb.utils.contains("TUNE_FEATURES", "bigendian", "armeb", "arm" ,d)}"

ENDSUFX = "${@bb.utils.contains("TUNE_FEATURES", "bigendian", "b", "" ,d)}"

TUNEVALID += "fpu-hard"
TARGET_FPU = "${@bb.utils.contains("TUNE_FEATURES", "fpu-hard", "hard", "soft" ,d)}"

