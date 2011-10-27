DEFAULTTUNE ?= "atom"
TUNE_PKGARCH ?= "${@bb.utils.contains("TUNE_FEATURES", "m32", "atom", "atom-64", d)}"

require conf/machine/include/tune-i586.inc

# Extra tune features
TUNEVALID[atom] = "Enable atom-specific processor optimizations"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "atom", "-march=atom -mssse3 -mfpmath=sse", "", d)}"

# Extra tune selections
AVAILTUNES += "atom"
TUNE_FEATURES_tune-atom ?= "${TUNE_FEATURES_tune-x86} atom"
BASE_LIB_tune-atom ?= "lib"
PACKAGE_EXTRA_ARCHS_tune-atom = "${PACKAGE_EXTRA_ARCHS_tune-x86} i386 i486 i586 i686 atom"

AVAILTUNES += "atom-64"
TUNE_FEATURES_tune-atom-64 ?= "${TUNE_FEATURES_tune-x86-64} atom"
BASE_LIB_tune-atom-64 ?= "lib64"
PACKAGE_EXTRA_ARCHS_tune-atom-64 = "${PACKAGE_EXTRA_ARCHS_tune-x86-64} atom-64"

AVAILTUNES += "atom-64-x32"
TUNE_FEATURES_tune-atom-64-x32 ?= "${TUNE_FEATURES_tune-x86-64-x32} atom"
BASE_LIB_tune-atom-64-x32 ?= "libx32"
PACKAGE_EXTRA_ARCHS_tune-atom-64-x32 = "${PACKAGE_EXTRA_ARCHS_tune-x86-64-x32} atom-64-x32"
