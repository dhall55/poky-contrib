DEFAULTTUNE ?= "ivb"
TUNE_PKGARCH ?= "${@bb.utils.contains("TUNE_FEATURES", "ivb", "ivb", "", d)}"

require conf/machine/include/tune-x86_64.inc

TUNEVALID[ivb] = "Enable ivb-specific processor optimizations"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "ivb", "-march=core-avx-i", "", d)}"

AVAILTUNES += "ivb"
TUNE_FEATURES_tune-ivb = "${TUNE_FEATURES_tune-x86-64} ivb"
PACKAGE_EXTRA_ARCHS_tune-ivb = "${PACKAGE_EXTRA_ARCHS_tune-x86-64} ivb"
