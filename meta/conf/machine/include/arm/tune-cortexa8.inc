# Enable Cortex-A8 tunings
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[cortexa8] = "Enable Cortex-A8 specific processor optimizations"

AVAILTUNES += "cortexa8 cortexa8t"

TUNENAME = "cortexa8"

TUNE_FEATURES_tune-cortexa8 = "${TUNE_FEATURES_tune-armv7a} coretexa8"
TUNE_FEATURES_tune-cortexa8t = "${TUNE_FEATURES_tune-armv7at} coretexa8"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "cortexa8", "-mtune=cortex-a8", "", d)}"

# Process has thumb, so armv7t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-cortexa8  = "${PACKAGE_EXTRA_ARCHS_tune-armv7at}"
PACKAGE_EXTRA_ARCHS_tune-cortexa8t = "${PACKAGE_EXTRA_ARCHS_tune-armv7at}"
