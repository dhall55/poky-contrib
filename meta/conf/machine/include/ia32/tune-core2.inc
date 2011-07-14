# Enable core2 tunings, and compatibility with i586
require conf/machine/include/ia32/tune-i586.inc

TUNEVALID[core2] = "Enable core2 specific processor optimizations"

AVAILTUNES += "core2 core2-64"

TUNENAME = "core2"

TUNE_FEATURES_tune-core2    ?= "${TUNE_FEATURES_tune-x86} core2"
TUNE_FEATURES_tune-core2-64 ?= "${TUNE_FEATURES_tune-x86-64} core2"

TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "core2", "-march=core2 -msse3 -mtune=generic -mfpmath=sse", "", d)}"

TUNE_ARCH	 = "${@bb.utils.contains("TUNE_FEATURES", "m32", "i686", "x86_64", d)}"
TUNE_PKGARCH	 = "${@bb.utils.contains("TUNE_FEATURES", "m32", "core2", "core2-64", d)}"

BASE_LIB_tune-core2    = "lib"
BASE_LIB_tune-core2-64 = "lib64"

PACKAGE_EXTRA_ARCHS_tune-core2 = "${PACKAGE_EXTRA_ARCHS_tune-x86} i386 i486 i586 i686 core2"
PACKAGE_EXTRA_ARCHS_tune-core2-64 = "${PACKAGE_EXTRA_ARCHS_tune-x86-64} core2-64"
