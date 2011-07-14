# Enable Cortex-M1 tunings
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[cortexm1] = "Enable Cortex-M1 specific processor optimizations"

AVAILTUNES += "cortexm1 cortexm1t"

TUNENAME = "cortexm1"

TUNE_FEATURES_tune-cortexm1 = "${TUNE_FEATURES_tune-armv7} coretexm1"
TUNE_FEATURES_tune-cortexm1t = "${TUNE_FEATURES_tune-armv7t} coretexm1"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "cortexm1", "-mtune=cortex-m1", "", d)}"

# Process has thumb, so armv7t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-cortexm1  = "${PACKAGE_EXTRA_ARCHS_tune-armv7t}"
PACKAGE_EXTRA_ARCHS_tune-cortexm1t = "${PACKAGE_EXTRA_ARCHS_tune-armv7t}"
