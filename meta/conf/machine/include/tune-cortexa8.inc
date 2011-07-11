require conf/machine/include/tune-armv7.inc

TUNENAME = "cortexa8"
TUNE_FEATURES_tune-cortexa8 ??= "hard-fpu neon"

TUNE_PKGARCH = "armv7a"

# Instead of using -mfpu=vfp[2] we can use -mfpu=neon to make use of gcc intrinsics[1] and vectorize loops with -ftree-vectorize[3]
# [1] http://gcc.gnu.org/onlinedocs/gcc/ARM-NEON-Intrinsics.html
# [2] http://gcc.gnu.org/onlinedocs/gcc/ARM-Options.html 
# [3] https://support.codesourcery.com/GNUToolchain/kbentry29
MAINOPTFLAGS ?= "-march=armv7-a -mtune=cortex-a8 -fno-tree-vectorize"

# Other potentially useful options
#-ftree-vectorize -ffast-math -fno-omit-frame-pointer

PACKAGE_EXTRA_ARCHS += "armv7a${ENDSUFX}${ARMSFX}"


