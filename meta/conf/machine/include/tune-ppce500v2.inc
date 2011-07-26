DEFAULTTUNE ?= "ppce500v2"

require conf/machine/include/powerpc/arch-powerpc.inc

TUNEVALID[ppce500mc] = "Enable ppce500mc specific processor optimizations"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "ppce500v2", "-mcpu=8548", "", d)}"
TUNE_PKGARCH .= "${@bb.utils.contains("TUNE_FEATURES", "ppce500v2", "ppce500v2", "", d)}"

AVAILTUNES += "ppce500v2"
TUNE_FEATURES_tune-ppce500v2 = "m32 spe ppce500v2"
PACKAGE_EXTRA_ARCHS_tune-ppce500v2 = "powerpc ppce500v2"
