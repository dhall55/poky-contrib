DEFAULTTUNE ?= "corei7"
TUNE_PKGARCH ?= "${@bb.utils.contains("TUNE_FEATURES", "avx", "corei7-avx", "corei7", d)}"

require conf/machine/include/tune-x86_64.inc

TUNEVALID[corei7] = "Enable corei7-specific processor optimizations"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "corei7", "-march=corei7${COREI7_AVX}", "", d)}"

COREI7_AVX = "${@bb.utils.contains("TUNE_FEATURES", [ "corei7", "avx" ], "-avx", "", d)}"

AVAILTUNES += "corei7"
TUNE_FEATURES_tune-corei7 = "${TUNE_FEATURES_tune-x86-64} corei7"
PACKAGE_EXTRA_ARCHS_tune-corei7 = "${PACKAGE_EXTRA_ARCHS_tune-x86-64} corei7"

AVAILTUNES += "corei7-avx"
TUNE_FEATURES_tune-corei7-avx = "${TUNE_FEATURES_tune-x86-64} corei7 avx"
PACKAGE_EXTRA_ARCHS_tune-corei7-avx = "${PACKAGE_EXTRA_ARCHS_tune-x86-64} corei7-avx"
