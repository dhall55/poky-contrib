# The ARCH name is made up of:
#   arm<architecture><features><abi><endian>
# 
# ARM Architecture:
#   4 -- Oldest we support, StrongARM, ARM7TDMI...
#   5 -- 926ej-s, XScale and similar (compat w/ 4)
#   6 -- arm1136jf-s and similar (compat w/ 5)
#   7 -- Cortex-m1, Cortext-m3 (compat w/ 6)
#   7a -- Cortex-a8 (Compat w/ 7)
#   7r -- Cortex-r4
#
# ARM features:
#  (In display order)
#   t = thumb ISA [armv5 and below]
#   t2 = thumb2 addition [armv6 and above]
#   j = Jazelle extensions [not referenced in our tunings]
#   e = DSP extensions [armv5]
#
# ABI:
#  While non-standard, we also add in an ABI suffix of "hf" in order to
#  specify when the EABI VFP register calling convention is enabled.
#
# Endian:
#  a 'b' is tacked on if the architecture is running in big-endian.
#
# Examples:  armv5teb, armv4t, armv6t2, armv7at2

ARM_ARCH = "arm"
ARM_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "armv4", "v4", "", d)}"
ARM_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "armv5", "v5", "", d)}"
ARM_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "armv6", "v6", "", d)}"
ARM_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "armv7", "v7", "", d)}"
ARM_ARCH .= "${@bb.utils.contains("TUNE_FEATURES", "armv7a", "-a", "", d)}"

# ARM_THUMB is defined in the feature-arm-thumb

ARM_DSP    = "${@bb.utils.contains("TUNE_FEATURES", [ "armv5", "dsp" ], "e", "", d)}"

ARM_ENDIAN = "${@bb.utils.contains("TUNE_FEATURES", "bigendian", "b", "", d)}"

TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "arm", bb.utils.contains("TUNE_FEATURES", "armv7", "-march=${ARM_ARCH}", "-march=${ARM_ARCH}${ARM_THUMB}${ARM_DSP}", d), "", d)}"
TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "bigendian", "-mbig-endian", "", d)}"

