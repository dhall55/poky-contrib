DEFAULTTUNE ?= "powerpc64"

require conf/machine/include/powerpc/arch-powerpc.inc

TUNEVALID[ppc-m64] = "Power ELF64 standard ABI"
TUNE_CONFLICTS[ppc-m64] = "ppc-m32 ppc-nf"
TUNE_FEATURE_CCARGS-ppc-m64 ?= "-m64"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "ppc-m64", "${TUNE_FEATURE_CCARGS-ppc-m64}", "", d)}"
TUNE_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", [ "ppc-m64" ], "powerpc64", "", d)}"

AVAILTUNES += "powerpc64"
TUNE_FEATURES_tune-powerpc64 ?= "ppc-m64 ppc-fpu-hard"
BASE_LIB_tune-powerpc64 = "lib64"
