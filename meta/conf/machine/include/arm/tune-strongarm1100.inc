# Tuning for the StrongArm 1100
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[strongarm1100] = "Enable instructions for StrongArm 1100"

AVAILTUNES += "strongarm1100"

TUNENAME = "strongarm1100"

TUNE_FEATURES_tune-strongarm1100 = "armv4 strongarm1100"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "strongarm1100", "-mtune=strongarm1100", "", d)}"

PACKAGE_EXTRA_ARCHS_tune-strongarm1100  = "${PACKAGE_EXTRA_ARCHS_tune-armv4}"
