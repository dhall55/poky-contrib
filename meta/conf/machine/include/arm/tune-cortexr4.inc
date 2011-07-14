# Enable Cortex-R4 tunings
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[armv7r] = "Enable instructions for ARMv7-r"
TUNEVALID[cortexr4] = "Enable Cortex-R4 specific processor optimizations"

AVAILTUNES += "cortexr4 cortexr4t"

TUNENAME = "cortexr4"

# "armv7" will already have been caught, add midding r
ARCH_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "armv7r", "-r", "", d)}"

TUNE_FEATURES_tune-cortexr4 = "${TUNE_FEATURES_tune-armv7} armv7r coretexr4"
TUNE_FEATURES_tune-cortexr4t = "${TUNE_FEATURES_tune-armv7t} armv7r coretexr4"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "cortexr4", "-mtune=cortex-r4", "", d)}"

# Process has thumb, so armv7t is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-cortexr4  = "${PACKAGE_EXTRA_ARCHS_tune-armv7t}"
PACKAGE_EXTRA_ARCHS_tune-cortexr4t = "${PACKAGE_EXTRA_ARCHS_tune-armv7t}"
