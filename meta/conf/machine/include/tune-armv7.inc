require conf/machine/include/arch-arm.inc
require conf/machine/include/feature-arm-thumb.inc
require conf/machine/include/feature-arm-hardfp.inc
require conf/machine/include/feature-arm-vfp.inc

TUNENAME = "armv7"
TUNE_FEATURES_tune-armv7 ??= "fpu-hard"

TUNE_PKGARCH = "armv7${ARMSFX}"

# valid options for -march: `armv7', `armv7-a', `armv7-r', `armv7-m'
# valid option for -mtune: `cortex-a8', `cortex-r4', `cortex-m3', `cortex-m1'
# This will NOT compile programs in 'ARM' mode, which is what you really want
MAINOPTFLAGS ?= "-march=armv7"

TARGET_CC_ARCH += "${MAINOPTFLAGS}"
PACKAGE_EXTRA_ARCHS = "${TUNE_ARCH}${ARMSFX} armv4${ENDSUFX}${ARMSFX} armv4t${ENDSUFX}${ARMSFX} armv5te${ENDSUFX}${ARMSFX} armv6${ENDSUFX}${ARMSFX} armv7${ENDSUFX}${ARMSFX}"

