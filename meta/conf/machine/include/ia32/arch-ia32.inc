# IA32 Architecture definition
# Two defined ABIs:
# *) ELF32
# *) ELF64

# Define arch specific tunings
TUNEVALID[m32] = "IA32 ELF32 standard ABI"
TUNEVALID[m64] = "IA32e (x86_64) ELF64 standard ABI"

# m32 & m64 are mutually exclusive
TUNECONFLICT[m32] = "m64"
TUNECONFLICT[m64] = "m32"

# Defined Tunes
AVAILTUNES += "x86 x86-64"

TUNE_FEATURES_tune-x86   ?= "m32"
TUNE_FEATURES_tune-x86-64 ?= "m64"

# Select a reasonable default
TUNENAME ?= "x86"

# m32:
TUNE_ARCH      .= "${@bb.utils.contains("TUNE_FEATURES", "m32", "i586", "" ,d)}"
TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "m32", "-m32", "", d)}"
BASE_LIB_tune-x86 = "lib"

# m64:
TUNE_ARCH      .= "${@bb.utils.contains("TUNE_FEATURES", "m64", "x86_64", "" ,d)}"
TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "m64", "-m64", "", d)}"
BASE_LIB_tune-x86-64 = "lib64"

TARGET_FPU	= "hard"

TUNE_PKGARCH		= "${@bb.utils.contains("TUNE_FEATURES", "m32", "x86", "x86_64", d)}"
PACKAGE_EXTRA_ARCHS	= "${@bb.utils.contains("TUNE_FEATURES", "m32", "x86", "x86_64", d)}"
