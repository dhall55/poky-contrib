#    The instruction set the compiler should use when generating application
#    code.  The kernel is always compiled with arm code at present.  arm code
#    is the original 32 bit ARM instruction set, thumb code is the 16 bit
#    encoded RISC sub-set.  Thumb code is smaller (maybe 70% of the ARM size)
#    but requires more instructions (140% for 70% smaller code) so may be
#    slower.

# Note armv7 will hit on armv7a as well
ARM_THUMB .= "${@bb.utils.contains("TUNE_FEATURES", [ "armv4", "thumb" ], "t", "", d)}"
ARM_THUMB .= "${@bb.utils.contains("TUNE_FEATURES", [ "armv5", "thumb" ], "t", "", d)}"
ARM_THUMB .= "${@bb.utils.contains("TUNE_FEATURES", [ "armv6", "thumb" ], "t2", "", d)}"
ARM_THUMB .= "${@bb.utils.contains("TUNE_FEATURES", [ "armv7", "thumb" ], "t2", "", d)}"

TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "thumb", "-mthumb", "-mno-thumb", d)}"
OVERRIDE       .= "${@bb.utils.contains("TUNE_FEATURES", "thumb", ":thumb", "", d)}"

#    Whether to compile with code to allow interworking between the two
#    instruction sets.  This allows thumb code to be executed on a primarily
#    arm system and vice versa.  It is strongly recommended that DISTROs not
#    turn this off - the actual cost is very small.
#
TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "no-thumb-interwork", "-mno-thumb-interwork", "-mthumb-interwork", d)}"
OVERRIDE       .= "${@bb.utils.contains("TUNE_FEATURES", "no-thumb-interwork", ":thumb-interwork", "", d)}"

TARGET_CC_KERNEL_ARCH  += "-mno-thumb-interwork -mno-thumb"
