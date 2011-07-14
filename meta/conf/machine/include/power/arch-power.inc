# Power Architecture definition
# Four defined ABIs, all combinations of:
# *) Hard/Soft Floating Point
# *) 32-bit/64-bit

TUNEVALID[fpu-hard] = "Use hardware FPU."
TUNEVALID[m32] = "Power ELF32 standard ABI"
TUNEVALID[m64] = "Power ELF64 standard ABI"

# Define tunes
AVAILTUNES += "powerpc powerpc64 powerpc-nf powerpc64-nf"

TUNE_FEATURES_tune-powerpc	?= "m32 fpu-hard"
TUNE_FEATURES_tune-powerpc64	?= "m64 fpu-hard"
TUNE_FEATURES_tune-powerpc-nf	?= "m32"
TUNE_FEATURES_tune-powerpc64-nf	?= "m64"

# Select a reasonable default
TUNENAME ?= "powerpc"

# Define canonical arch
TUNE_ARCH	 = "${@bb.utils.contains("TUNE_FEATURES", [ "m64" ], "powerpc64", "powerpc", d)}"

# ABI
TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "m32", "-m32", "", d)}"
TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "n64", "-m64", "", d)}"

# Floating Point
TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "fpu-hard", "-mhard-float", "-msoft-float", d)}"
TARGET_FPU	 = "${@bb.utils.contains("TUNE_FEATURES", "fpu-hard", "hard", "soft", d)}"

# Base library directory
BASE_LIB_tune-powerpc	   = "lib"
BASE_LIB_tune-powerpc64	   = "lib64"
BASE_LIB_tune-powerpc-nf   = "lib"
BASE_LIB_tune-powerpc64-nf = "lib64"
