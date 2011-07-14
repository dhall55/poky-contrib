# MIPS Architecture definition
# 12 defined ABIs, all combinations of:
# *) Big/Little Endian
# *) Hardware/Software Floating Point
# *) o32, n32, n64 ABI

TUNEVALID[bigendian] = "Enable big-endian mode."
TUNEVALID[fpu-hard] = "Use hardware FPU."
TUNEVALID[o32] = "MIPS o32 ABI"
TUNEVALID[n32] = "MIPS64 n32 ABI"
TUNEVALID[n64] = "MIPS64 n64 ABI"
TUNECONFLICT[o32] = "n32 n64"
TUNECONFLICT[n32] = "o32 n64"
TUNECONFLICT[n64] = "o32 n32"

# Defined tunes
AVAILTUNES += "mips mips64-n32 mips64 mipsel mips64el-n32 mips64el mips-nf mips64-nf-n32 mips64-nf mipsel-nf mips64el-nf-n32 mips64el-nf"

TUNE_FEATURES_tune-mips = "o32 bigendian fpu-hard"
TUNE_FEATURES_tune-mips64-n32 = "n32 bigendian fpu-hard"
TUNE_FEATURES_tune-mips64 = "n64 bigendian fpu-hard"
TUNE_FEATURES_tune-mipsel = "o32 fpu-hard"
TUNE_FEATURES_tune-mips64el-n32 = "n32 fpu-hard"
TUNE_FEATURES_tune-mips64el = "n64 fpu-hard"
TUNE_FEATURES_tune-mips-nf = "o32 bigendian"
TUNE_FEATURES_tune-mips64-nf-n32 = "n32 bigendian"
TUNE_FEATURES_tune-mips64-nf = "n64 bigendian"
TUNE_FEATURES_tune-mipsel-nf = "o32"
TUNE_FEATURES_tune-mips64el-nf-n32 = "n32"
TUNE_FEATURES_tune-mips64el-nf = "n64"

# Select a reasonable default
TUNENAME ?= "mips"

# Define canonical arch
TUNE_ENDIAN_SUFX = "${@bb.utils.contains("TUNE_FEATURES", "bigendian", "", "el", d)}"
TUNE_BYTE_SUFX	 = "${@bb.utils.contains("TUNE_FEATURES", [ "n32, "n64" ], "64", "", d)}"

TUNE_ARCH = "mips${TUNE_BYTE_SUFX}${TUNE_ENDIAN_SUFX}"

# ABI
TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "o32", "-mabi=32", "", d)}"
TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "n32", "-mabi=n32", "", d)}"
TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "n32", "-mabi=64", "", d)}"

# Floating Point
TARGET_CC_ARCH	+= "${@bb.utils.contains("TUNE_FEATURES", "fpu-hard", "-mhard-float", "-msoft-float", d)}"
TARGET_FPU	 = "${@bb.utils.contains("TUNE_FEATURES", "fpu-hard", "hard", "soft", d)}"

# Endian
TARGET_CC_ARCH 	+= "${@bb.utils.contains("TUNE_FEATURES", "bigendian", "-meb", "-mel", d)}"

# Base library directory
BASE_LIB_tune-mips = "lib"
BASE_LIB_tune-mips64-n32 = "lib32"
BASE_LIB_tune-mips64 = "lib64"
BASE_LIB_tune-mipsel = "lib"
BASE_LIB_tune-mips64el-n32 = "lib32"
BASE_LIB_tune-mips64el = "lib64"
BASE_LIB_tune-mips-nf = "lib"
BASE_LIB_tune-mips64-nf-n32 = "lib32"
BASE_LIB_tune-mips64-nf = "lib64"
BASE_LIB_tune-mipsel-nf = "lib"
BASE_LIB_tune-mips64el-nf-n32 = "lib32"
BASE_LIB_tune-mips64el-nf = "lib64"
