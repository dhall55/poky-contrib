require conf/machine/include/arch-ia32.inc

TUNENAME = "atom"
TUNE_FEATURES_tune-atom ??= ""

TUNE_PKGARCH = "core2"

TARGET_CC_ARCH = "-m32 -march=core2 -msse3 -mtune=generic -mfpmath=sse"
TARGET_CC_ARCH_ml-tune-lib64 = "-m64 -march=core2 -msse3 -mtune=generic -mfpmath=sse"

PACKAGE_EXTRA_ARCHS = "x86 i386 i486 i586 i686 core2"
