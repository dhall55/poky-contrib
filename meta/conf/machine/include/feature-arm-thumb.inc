#    The instruction set the compiler should use when generating application
#    code.  The kernel is always compiled with arm code at present.  arm code
#    is the original 32 bit ARM instruction set, thumb code is the 16 bit
#    encoded RISC sub-set.  Thumb code is smaller (maybe 70% of the ARM size)
#    but requires more instructions (140% for 70% smaller code) so may be
#    slower.
TUNEVALID += "thumb-instructions"
TARGET_CC_ARCH +=  "${@bb.utils.contains("TUNE_FEATURES", "thumb-instructions", "-mthumb", "-mno-thumb" ,d)}"
OVERRIDES .= "${@bb.utils.contains("TUNE_FEATURES", "thumb-instructions", ":thumb", "" ,d)}

#    Whether to compile with code to allow interworking between the two
#    instruction sets.  This allows thumb code to be executed on a primarily
#    arm system and vice versa.  It is strongly recommended that DISTROs not
#    turn this off - the actual cost is very small.
TUNEVALID += "thumb-interwork"
TARGET_CC_ARCH +=  "${@bb.utils.contains("TUNE_FEATURES", "thumb-interwork", "-mthumb-interwork", "-mno-thumb-interwork" ,d)}"
OVERRIDES .= "${@bb.utils.contains("TUNE_FEATURES", "thumb-interwork", ":thumb-interwork", "" ,d)}

TARGET_CC_KERNEL_ARCH  += "-mno-thumb-interwork -mno-thumb"

