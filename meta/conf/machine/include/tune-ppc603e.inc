require conf/machine/include/arch-powerpc.inc

TUNENAME = "ppc603e"

TUNE_PKGARCH = "ppc603e"

TARGET_CC_ARCH = "-mcpu=603e  -mhard-float"

PACKAGE_EXTRA_ARCHS = "powerpc ppc603e"
