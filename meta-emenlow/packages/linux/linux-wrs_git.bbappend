FILESPATH_emenlow := "${FILESPATH}:${@os.path.dirname(bb.data.getVar('FILE', d, True))}"
SRC_URI_append_emenlow += "file://defconfig"
COMPATIBLE_MACHINE_emenlow = "emenlow"
WRMACHINE_emenlow  = "emenlow"
