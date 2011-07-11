TUNEVALID += "neon"
TARGET_FPU = "${@bb.utils.contains("TUNE_FEATURES", "neon", "-mfpu=neon", "-mfpu=vfp" ,d)}"
ARMSFX .= "${@bb.utils.contains("TUNE_FEATURES", "neon", "", "-vfponly" ,d)}"
