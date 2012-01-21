# Power Architecture definition
# Four defined ABIs, all combinations of:
# *) Hard/Soft Floating Point
# *) 32-bit/64-bit

DEFAULTTUNE ?= "powerpc"

TUNEVALID[ppc-m32] = "Power ELF32 standard ABI"
TUNE_FEATURE_CCARGS-ppc-m32 ?= "-m32"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "ppc-m32", "${TUNE_FEATURE_CCARGS-ppc-m32}", "", d)}"
TUNE_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "ppc-m32", "powerpc", "", d)}"

TUNEVALID[ppc-fpu-hard] = "Use hardware FPU."
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "ppc-fpu-hard", "-mhard-float", "", d)}"

TUNEVALID[ppc-fpu-soft] = "Use software FPU."
TUNE_FEATURE_CCARGS-ppc-fpu-soft ?= "-msoft-float"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "ppc-fpu-soft", "${TUNE_FEATURE_CCARGS-ppc-fpu-soft}", "", d)}"
TARGET_FPU .= "${@bb.utils.contains("TUNE_FEATURES", "ppc-fpu-soft", "soft", "", d)}"

ABIEXTENSION = "${@['','spe'][d.getVar('TARGET_FPU', True) in ['ppc-efd', 'ppc-efs']]}"

PPCPKGSFX_FPU = "${@bb.utils.contains("TUNE_FEATURES", "ppc-fpu-hard" , "", "-nf", d)}"

PPCPKGARCH = "${TUNE_ARCH}${PPCPKGSFX_FPU}"
TUNE_PKGARCH ?= "${PPCPKGARCH}"

# Basic tune definitions
AVAILTUNES += "powerpc powerpc-nf" 
TUNE_FEATURES_tune-powerpc-nf ?= "ppc-m32 ppc-fpu-soft"
BASE_LIB_tune-powerpc-nf = "lib"
PACKAGE_EXTRA_ARCHS_tune-powerpc-nf = "powerpc-nf"
TUNE_FEATURES_tune-powerpc ?= "ppc-m32 ppc-fpu-hard"
BASE_LIB_tune-powerpc = "lib"
PACKAGE_EXTRA_ARCHS_tune-powerpc = "${PACKAGE_EXTRA_ARCHS_tune-powerpc-nf} powerpc"


