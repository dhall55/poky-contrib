# Power Architecture definition
# Four defined ABIs, all combinations of:
# *) Hard/Soft Floating Point
# *) 32-bit/64-bit

DEFAULTTUNE ?= "powerpc"

TUNEVALID[m32] = "Power ELF32 standard ABI"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "m32", "-m32", "", d)}"

TUNEVALID[m32-arch] = "Enable powerpc package architecture"
TUNE_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", [ "m32-arch" ], "powerpc", "", d)}"

TUNEVALID[m64] = "Power ELF64 standard ABI"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "n64", "-m64", "", d)}"

TUNEVALID[m64-arch] = "Enable powerpc64 package architecture"
TUNE_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", [ "m64-arch" ], "powerpc64", "", d)}"

TUNEVALID[fpu-hard] = "Use hardware FPU."
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "fpu-hard", "-mhard-float", "", d)}"

TUNEVALID[fpu-soft] = "Use software FPU."
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "fpu-soft", "-msoft-float", "", d)}"
TARGET_FPU .= "${@bb.utils.contains("TUNE_FEATURES", "fpu-soft", "soft", "", d)}"

TUNEVALID[spe] = "Enable SPE ABI extensions"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "spe", "-mabi=spe -mspe", "", d)}"

ABIEXTENSION = "${@['','spe'][d.getVar('TARGET_FPU', True) in ['ppc-efd', 'ppc-efs']]}"

TUNE_PKGARCH ?= "${TUNE_ARCH}"

# Basic tune definitions
AVAILTUNES += "powerpc powerpc-nf" 
TUNE_FEATURES_tune-powerpc ?= "m32 m32-arch fpu-hard"
BASE_LIB_tune-powerpc = "lib"
TUNE_FEATURES_tune-powerpc-nf ?= "m32 m32-arch fpu-soft"
BASE_LIB_tune-powerpc-nf = "lib"

AVAILTUNES += "powerpc64 powerpc64-nf"
TUNE_FEATURES_tune-powerpc64 ?= "m64 m64-arch fpu-hard"
BASE_LIB_tune-powerpc64 = "lib64"
TUNE_FEATURES_tune-powerpc64-nf ?= "m64 m64-arch fpu-soft"
BASE_LIB_tune-powerpc64-nf = "lib64"

