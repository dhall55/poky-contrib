# VFP compiler options are automatically selected
ARM_FPU 	= "${@bb.utils.contains("TUNE_FEATURES", "vfp", "-vfp", "" ,d)}"

# Handle Neon
ARM_FPU	       .= "${@bb.utils.contains("TUNE_FEATURES", "neon", "-neon", "" ,d)}"
TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "neon", "-mfpu=neon", "" ,d)}"

TARGET_FPU	= "${@d.getVar('ARM_FPU', True).strip('-') or 'soft'}"
