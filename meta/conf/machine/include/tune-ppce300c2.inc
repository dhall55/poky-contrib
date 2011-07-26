DEFAULTTUNE ?= "ppce300"

require conf/machine/include/powerpc/arch-powerpc.inc

TUNEVALID[ppce300] = "Enable ppce300 specific processor optimizations"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "ppce300", "-mcpu=e300c2", "", d)}"
TUNE_PKGARCH = "${@bb.utils.contains("TUNE_FEATURES", "ppce300", "ppce300", "${TUNE_ARCH}", d)}"

AVAILTUNES += "ppce300"
TUNE_FEATURES_tune-ppce300 = "m32 fpu-soft ppce300"
PACKAGE_EXTRA_ARCHS_tune-ppce300 = "powerpc ppce300"
