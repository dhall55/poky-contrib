# Enable 920t tunings
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[arm926ejs] = "Enable arm926ejs specific processor optimizations"

AVAILTUNES += "arm926ejs arm926ejst"

TUNENAME = "arm926ejs"

TUNE_FEATURES_tune-arm926ejs  = "${TUNE_FEATURES_tune-armv5e} arm926ejs"
TUNE_FEATURES_tune-arm926ejst = "${TUNE_FEATURES_tune-armv5te} arm926ejs"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "arm926ejs", "-mtune=arm926ej-s", "", d)}"

# Process has thumb, so armv4t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-arm926ejs  = "${PACKAGE_EXTRA_ARCHS_tune-armv5te}"
PACKAGE_EXTRA_ARCHS_tune-arm926ejst = "${PACKAGE_EXTRA_ARCHS_tune-armv5te}"
