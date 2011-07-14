# Enable arm9tdmi tunings
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[arm9tdmi] = "Enable arm9tdmi specific processor optimizations"

AVAILTUNES += "arm9dmi arm9tdmi"

TUNENAME = "arm9dmi"

TUNE_FEATURES_tune-arm9dmi  = "${TUNE_FEATURES_tune-armv4} arm9tdmi"
TUNE_FEATURES_tune-arm9tdmi = "${TUNE_FEATURES_tune-armv4t} arm9tdmi"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "arm9tdmi", "-mtune=arm9tdmi", "", d)}"

# Process has thumb, so armv4t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-arm9dmi  = "${PACKAGE_EXTRA_ARCHS_tune-armv4t}"
PACKAGE_EXTRA_ARCHS_tune-arm9tdmi = "${PACKAGE_EXTRA_ARCHS_tune-armv4t}"
