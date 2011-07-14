# Enable arm1136jf-s tunings
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[arm1136jfs] = "Enable arm1136jfs specific processor optimizations"

AVAILTUNES += "arm1136jfs arm1136jfst"

TUNENAME = "arm1136jfs"

TUNE_FEATURES_tune-arm1136jfs = "${TUNE_FEATURES_tune-armv6} arm1136jfs"
TUNE_FEATURES_tune-arm1136jfst = "${TUNE_FEATURES_tune-armv6t} arm1136jfs"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "arm1136jfs", "-mtune=arm1136jf-s", "", d)}"

# Process has thumb2, so armv6t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-arm1136jfs  = "${PACKAGE_EXTRA_ARCHS_tune-armv6t}"
PACKAGE_EXTRA_ARCHS_tune-arm1136jfst = "${PACKAGE_EXTRA_ARCHS_tune-armv6t}"
