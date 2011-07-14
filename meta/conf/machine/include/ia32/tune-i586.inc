# Enable i586 tunings
require conf/machine/include/ia32/arch-ia32.inc

TUNEVALID[i586] = "Enable i586 specific processor optimizations"

AVAILTUNES += "i586"

TUNENAME = "i586"

TUNE_FEATURES_tune-i586    ?= "${TUNE_FEATURES_tune-x86} i586"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "i586", "-march=i586", "", d)}"

TUNE_ARCH	 = "i586"
TUNE_PKGARCH	 = "i586"

BASE_LIB_tune-i586    = "lib"

PACKAGE_EXTRA_ARCHS_tune-i586 = "${TUNE_FEATURES_tune-x86} i386 i486 i586"
