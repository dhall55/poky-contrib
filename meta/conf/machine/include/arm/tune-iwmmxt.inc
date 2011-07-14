# Enable IWMMXT tunings for PXA27x Applications Processor Family
# Use tune-xscale for PXA255/PXA26x based processors.
require conf/machine/include/arm/arch-arm.inc

TUNEVALID[iwmmxt] = "Enable instructions for iwmmxt"

AVAILTUNES += "iwmmx iwmmxt"

TUNENAME = "iwmmx"

ARCH_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "iwmmxt", "iwmmxt", "", d)}"

TUNE_FEATURES_tune-iwmmx = "iwmmxt"
TUNE_FEATURES_tune-iwmmxt = "iwmmxt thumb"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "iwmmxt", "-mtune=iwmmxt", "", d)}"

# Process has thumb, so armv5te is compatible in all tunes
PACKAGE_EXTRA_ARCHS_tune-iwmmx  = "${PACKAGE_EXTRA_ARCHS_tune-armv5te} iwmmx"
PACKAGE_EXTRA_ARCHS_tune-iwmmxt = "${PACKAGE_EXTRA_ARCHS_tune-armv5te} iwmmxt"
