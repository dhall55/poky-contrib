# Enable 920t tunings
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[arm920t] = "Enable arm920t specific processor optimizations"

AVAILTUNES += "arm920 arm920t"

TUNENAME = "arm920"

TUNE_FEATURES_tune-arm920 = "${TUNE_FEATURES_tune-armv4} arm920t"
TUNE_FEATURES_tune-arm920t = "${TUNE_FEATURES_tune-armv4t} arm920t"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "arm920t", "-mtune=arm920t", "", d)}"

# Process has thumb, so armv4t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-arm920  = "${PACKAGE_EXTRA_ARCHS_tune-armv4t}"
PACKAGE_EXTRA_ARCHS_tune-arm920t = "${PACKAGE_EXTRA_ARCHS_tune-armv4t}"
