# Enable EP9312 tunings
#   has an arm920t core plus a Mavrick math engine
require conf/machine/include/arm/tune-arm920t.inc

TUNEVALID[ep9312] = "Enable instructions for ep9312"

AVAILTUNES += "ep9312 ep9312t"

TUNENAME = "ep9312"

ARCH_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "ep9312", "ep9312", "", d)}"

TUNE_FEATURES_tune-ep9312 = "ep9312"
TUNE_FEATURES_tune-ep9312t = "ep9312 thumb"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "ep9312", "-mtune=ep9312 -mfp=maverick", "", d)}"

# Process has thumb, so armv4t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-ep9312  = "${PACKAGE_EXTRA_ARCHS_tune-arm920t} ep9312"
PACKAGE_EXTRA_ARCHS_tune-ep9312t = "${PACKAGE_EXTRA_ARCHS_tune-arm920t} ep9312"
