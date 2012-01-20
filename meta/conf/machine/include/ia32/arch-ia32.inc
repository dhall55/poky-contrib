#
# IA32 Architecture definition
#

DEFAULTTUNE ?= "x86"
TARGET_FPU ?= ""
X86ARCH32 ?= "i586"
X86ARCH64 ?= "x86_64"

# ELF32 ABI
TUNEVALID[x86-m32] = "IA32 ELF32 standard ABI"
TUNECONFLICTS[x86-m32] = "x86-64-m64 x86-64-mx32"
TUNE_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "x86-m32", "${X86ARCH32}", "" ,d)}"
TUNE_FEATURE_CCARGS-x86-m32 ?= "-m32"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "x86-m32", "${TUNE_FEATURE_CCARGS-x86-m32}", "", d)}"
MACHINEOVERRIDES .= "${@bb.utils.contains("TUNE_FEATURES", "x86-m32", ":x86", "" ,d)}"

# x32 ABI
TUNEVALID[x86-64-mx32] = "IA32e (x86_64) ELF32 standard ABI"
TUNECONFLICTS[x86-64-mx32] = "x86-64-m64 x86-m32"
TUNE_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "x86-64-mx32", "${X86ARCH64}", "" ,d)}"
ABIEXTENSION .= "${@bb.utils.contains("TUNE_FEATURES", "x86-64-mx32", "x32", "" ,d)}"
TUNE_FEATURE_CCARGS-x86-64-mx32 ?= "-mx32"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "x86-64-mx32", "${TUNE_FEATURE_CCARGS-x86-64-mx32}", "", d)}"
TUNE_LDARGS += "${@bb.utils.contains("TUNE_FEATURES", "x86-64-mx32", "-m elf32_x86_64", "", d)}"
TUNE_ASARGS += "${@bb.utils.contains("TUNE_FEATURES", "x86-64-mx32", "-x32", "", d)}"

# ELF64 ABI
TUNEVALID[x86-64-m64] = "IA32e (x86_64) ELF64 standard ABI"
TUNECONFLICT[x86-64-m64] = "x86-m32 x86-64-mx32"
TUNE_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "x86-64-m64", "${X86ARCH64}", "" ,d)}"
TUNE_FEATURE_CCARGS-x86-64-m64 ?= "-m64"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "x86-64-m64", "${TUNE_FEATURE_CCARGS-x86-64-m64}", "", d)}"

TUNE_PKGARCH ?= "${@bb.utils.contains("TUNE_FEATURES", "x86-m32", "x86", "x86_64", d)}"

# Default Tune configurations
AVAILTUNES += "x86"
TUNE_FEATURES_tune-x86 ?= "x86-m32"
BASE_LIB_tune-x86 ?= "lib"
PACKAGE_EXTRA_ARCHS_tune-x86 = "x86"

AVAILTUNES += "x86-64"
TUNE_FEATURES_tune-x86-64 ?= "x86-64-m64"
BASE_LIB_tune-x86-64 ?= "lib64"
PACKAGE_EXTRA_ARCHS_tune-x86-64 = "x86_64"

AVAILTUNES += "x86-64-x32"
TUNE_FEATURES_tune-x86-64-x32 ?= "x86-64-mx32"
BASE_LIB_tune-x86-64-x32 ?= "libx32"
PACKAGE_EXTRA_ARCHS_tune-x86-64-x32 = "x86_64_x32"
TUNE_PKGARCH .= "${@bb.utils.contains("TUNE_FEATURES", "x86-64-mx32", "_x32", "", d)}"
