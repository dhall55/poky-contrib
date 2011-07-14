# Set both the software ABI and Floating Point ABI
#
# Core ABI is always EABI, note this is different from the unsupport
# OABI which used to be fairly common.
ABIEXTENSION 	= "eabi"

# The -mfloat-abi selects the EABI calling convention and internal floating
# point support.
#
# soft [default] - software calling convention, no fpu support
# softfp - software calling convention, fpu [vfp by default] support
# hard - hardware floating point (vfp) register calling convention

# If VFP is enabled, set hard or softfp based on calling convention
TARGET_CC_ARCH += "${@bb.utils.contains("TUNE_FEATURES", "vfp", bb.utils.contains("TUNE_FEATURES", "callconvention-hard", "-mfloat-abi=hard", "-mfloat-abi=softfp", d), "" ,d)}"

# Since EABI hard float is incompatible with soft float, we need to tag the packages as such
ARM_EABI = "${@bb.utils.contains("TUNE_FEATURES", [ "callconvention-hard", "vfp" ], "hf", "", d)}"
