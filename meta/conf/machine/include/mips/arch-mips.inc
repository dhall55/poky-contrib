# MIPS Architecture definition
# 12 defined ABIs, all combinations of:
# *) Big/Little Endian
# *) Hardware/Software Floating Point
# *) o32, n32, n64 ABI

DEFAULTTUNE ?= "mips"

# Endianess
TUNEVALID[mips-bigendian] = "Enable big-endian mode"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "mips-bigendian", "-meb", "-mel", d)}"

# ABI flags
TUNEVALID[mips-o32] = "MIPS o32 ABI"
TUNECONFLICT[mips-o32] = "mips-n32 mips-n64"
TUNE_FEATURE_CCARGS-mips-o32 ?= "-mabi=32"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "mips-o32", "${TUNE_FEATURE_CCARGS-mips-o32}", "", d)}"

TUNEVALID[mips-n32] = "MIPS64 n32 ABI"
TUNECONFLICT[mips-n32] = "mips-o32 mips-n64"
TUNE_FEATURE_CCARGS-mips-n32 ?= "-mabi=n32"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "mips-n32", "${TUNE_FEATURE_CCARGS-mips-n32}", "", d)}"

TUNEVALID[mips-n64] = "MIPS64 n64 ABI"
TUNECONFLICT[mips-n64] = "mips-o32 mips-n32"
TUNE_FEATURE_CCARGS-mips-n64 ?= "-mabi=64"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "mips-n64", "${TUNE_FEATURE_CCARGS-mips-n64}", "", d)}"

# Floating point
TUNEVALID[mips-fpu-hard] = "Use hardware FPU"
TUNE_CCARGS += "${@bb.utils.contains("TUNE_FEATURES", "mips-fpu-hard", "-mhard-float", "-msoft-float", d)}"
TARGET_FPU = "${@bb.utils.contains("TUNE_FEATURES", "mips-fpu-hard", "", "soft", d)}"

# Package naming
MIPSPKGSFX_ENDIAN = "${@bb.utils.contains("TUNE_FEATURES", "mips-bigendian", "", "el", d)}"
MIPSPKGSFX_BYTE = "${@bb.utils.contains("TUNE_FEATURES", "mips-n64" , "64", "", d)}"
MIPSPKGSFX_BYTE .= "${@bb.utils.contains("TUNE_FEATURES", "mips-n32" , "64", "", d)}"
MIPSPKGSFX_FPU = "${@bb.utils.contains("TUNE_FEATURES", "mips-fpu-hard" , "", "-nf", d)}"
MIPSPKGSFX_ABI = "${@bb.utils.contains("TUNE_FEATURES", "mips-n32", "-n32", "", d)}"

TUNE_ARCH = "mips${MIPSPKGSFX_BYTE}${MIPSPKGSFX_ENDIAN}"
TUNE_PKGARCH ?= "${TUNE_ARCH}${MIPSPKGSFX_FPU}${MIPSPKGSFX_ABI}"

# Base tunes
AVAILTUNES += "mips mips64-n32 mips64 mipsel mips64el-n32 mips64el mips-nf mips64-nf-n32 mips64-nf mipsel-nf mips64el-nf-n32 mips64el-nf"
TUNE_FEATURES_tune-mips = "mips-o32 mips-bigendian mips-fpu-hard"
BASE_LIB_tune-mips = "lib"
TUNE_FEATURES_tune-mips64-n32 = "mips-n32 mips-bigendian mips-fpu-hard"
BASE_LIB_tune-mips64-n32 = "lib32"
TUNE_FEATURES_tune-mips64 = "mips-n64 mips-bigendian mips-fpu-hard"
BASE_LIB_tune-mips64 = "lib64"
TUNE_FEATURES_tune-mipsel = "mips-o32 mips-fpu-hard"
BASE_LIB_tune-mipsel = "lib"
TUNE_FEATURES_tune-mips64el-n32 = "mips-n32 mips-fpu-hard"
BASE_LIB_tune-mips64el-n32 = "lib32"
TUNE_FEATURES_tune-mips64el = "mips-n64 mips-fpu-hard"
BASE_LIB_tune-mips64el = "lib64"
TUNE_FEATURES_tune-mips-nf = "mips-o32 mips-bigendian"
BASE_LIB_tune-mips-nf = "lib"
TUNE_FEATURES_tune-mips64-nf-n32 = "mips-n32 mips-bigendian"
BASE_LIB_tune-mips64-nf-n32 = "lib32"
TUNE_FEATURES_tune-mips64-nf = "mips-n64 mips-bigendian"
BASE_LIB_tune-mips64-nf = "lib64"
TUNE_FEATURES_tune-mipsel-nf = "mips-o32"
BASE_LIB_tune-mipsel-nf = "lib"
TUNE_FEATURES_tune-mips64el-nf-n32 = "mips-n32"
BASE_LIB_tune-mips64el-nf-n32 = "lib32"
TUNE_FEATURES_tune-mips64el-nf = "mips-n64"
BASE_LIB_tune-mips64el-nf = "lib64"

