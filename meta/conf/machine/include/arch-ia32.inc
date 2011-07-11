TUNEVALID += "m64"
TUNE_ARCH = "${@bb.utils.contains("TUNE_FEATURES", ["m64", "ml-lib64"], "x86_64", "i586" ,d)}"
TARGET_CC_ARCH +=  "${@bb.utils.contains("TUNE_FEATURES", ["m64", "ml-lib64"], "-m64", "-m32" ,d)}"

TUNEVALID += "ml-lib32"
TUNE_ARCH_ml-tune-lib32 = "i586"
base_libdir_ml-tune-lib32 = "/lib32"
libdir_ml-tune-lib32 = "/usr/lib32"
TUNEOVERRIDES .= "${@bb.utils.contains("TUNE_FEATURES", "ml-lib32", ":ml-tune-lib32", "", d)}"

TUNEVALID += "ml-lib64"
TUNE_ARCH_ml-tune-lib64 = "x86_64"
base_libdir_ml-tune-lib64 = "/lib64"
libdir_ml-tune-lib64 = "/usr/lib64"
TUNEOVERRIDES .= "${@bb.utils.contains("TUNE_FEATURES", "ml-lib64", ":ml-tune-lib64", "", d)}"

OVERRIDES .= "${TUNEOVERRIDES}"

GLIBC_ADDONS = "nptl"
GLIBC_EXTRA_OECONF = "--with-tls"
