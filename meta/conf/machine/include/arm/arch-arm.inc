# Arm is a fairly complex architecture family.  Within the arch-arm we define
# the core ARCH definition, features such as fpu settings (vfp/neon), and
# thumb (thumb2).

# ARM Architecture definition
# Four defined ABIs:
# *) Little Endian - EABI Soft Float calling
# *) Little Endian - EABI Hard Float calling
# *) Big Endian - EABI Soft Float calling
# *) Big Endian - EABI Hard Float calling

TUNEVALID[armv4] = "Enable instructions for ARMv4"
TUNEVALID[armv5] = "Enable instructions for ARMv5"
TUNEVALID[armv6] = "Enable instructions for ARMv6"
TUNEVALID[armv7] = "Enable instructions for ARMv7"
TUNEVALID[armv7a] = "Enable instructions for ARMv7-a"

TUNEVALID[thumb] = "Enable thumb & thumb interworking."
TUNEVALID[no-thumb-interworking] = "Disable thumb interworking."
TUNEVALID[dsp] = "Enable DSP extensions [armv5]"
TUNEVALID[bigendian] = "Enable big-endian mode."

TUNEVALID[vfp] = "Enable Vector Floating Point (vfp) unit."
TUNEVALID[neon] = "Enable Neon SIMD accelerator unit."

TUNEVALID[callconvention-hard] = "Enable EABI hard float call convention, requires VFP."

# Base Little Endian tunes -- all reasonable combos
AVAILTUNES += "armv4 armv4t armv5 armv5t armv5e armv5te armv5-vfp armv5t-vfp armv5e-vfp armv5te-vfp"
AVAILTUNES += "armv6 armv6t armv7 armv7t armv7-neon armv7t-neon armv7a armv7at armv7a-neon armv7at-neon"
TUNE_FEATURES_tune-armv4		?= "armv4"
TUNE_FEATURES_tune-armv4t		?= "armv4 thumb"
TUNE_FEATURES_tune-armv5		?= "armv5"
TUNE_FEATURES_tune-armv5t		?= "armv5 thumb"
TUNE_FEATURES_tune-armv5e		?= "armv5 dsp"
TUNE_FEATURES_tune-armv5te		?= "armv5 dsp thumb"
TUNE_FEATURES_tune-armv5-vfp		?= "armv5 vfp"
TUNE_FEATURES_tune-armv5t-vfp		?= "armv5 vfp"
TUNE_FEATURES_tune-armv5e-vfp		?= "armv5 vfp dsp"
TUNE_FEATURES_tune-armv5te-vfp		?= "armv5 vfp dsp thumb"
TUNE_FEATURES_tune-armv6		?= "armv6 vfp"
TUNE_FEATURES_tune-armv6t		?= "armv6 vfp thumb"
TUNE_FEATURES_tune-armv7		?= "armv7 vfp"
TUNE_FEATURES_tune-armv7t		?= "armv7 vfp thumb"
TUNE_FEATURES_tune-armv7-neon		?= "armv7 vfp neon"
TUNE_FEATURES_tune-armv7t-neon		?= "armv7 vfp neon thumb"
TUNE_FEATURES_tune-armv7a		?= "armv7a vfp"
TUNE_FEATURES_tune-armv7at		?= "armv7a vfp thumb"
TUNE_FEATURES_tune-armv7a-neon		?= "armv7a vfp neon"
TUNE_FEATURES_tune-armv7at-neon		?= "armv7a vfp neon thumb"

# Little Endian Hardware Floating ABI tunes
# Requires VFP support
AVAILTUNES += "armv5hf-vfp armv5thf-vfp armv5ehf-vfp armv5tehf-vfp armv6hf armv6thf"
AVAILTUNES += "armv7hf armv7thf armv7hf-neon armv7thf-neon armv7ahf armv7ahf-neon armv7athf-neon"
TUNE_FEATURES_tune-armv5hf-vfp		?= "${TUNE_FEATURES_tune-armv5-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv5thf-vfp		?= "${TUNE_FEATURES_tune-armv5t-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv5ehf-vfp		?= "${TUNE_FEATURES_tune-armv5e-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv5tehf-vfp	?= "${TUNE_FEATURES_tune-armv5te-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv6hf		?= "${TUNE_FEATURES_tune-armv6} callconvention-hard"
TUNE_FEATURES_tune-armv6thf		?= "${TUNE_FEATURES_tune-armv6t} callconvention-hard"
TUNE_FEATURES_tune-armv7hf		?= "${TUNE_FEATURES_tune-armv7} callconvention-hard"
TUNE_FEATURES_tune-armv7thf		?= "${TUNE_FEATURES_tune-armv7t} callconvention-hard"
TUNE_FEATURES_tune-armv7hf-neon		?= "${TUNE_FEATURES_tune-armv7-neon} callconvention-hard"
TUNE_FEATURES_tune-armv7thf-neon	?= "${TUNE_FEATURES_tune_armv7t-neon} callconvention-hard"
TUNE_FEATURES_tune-armv7ahf		?= "${TUNE_FEATURES_tune_armv7a} callconvention-hard"
TUNE_FEATURES_tune-armv7athf		?= "${TUNE_FEATURES_tune_armv7at} callconvention-hard"
TUNE_FEATURES_tune-armv7ahf-neon	?= "${TUNE_FEATURES_tune_armv7a} callconvention-hard"
TUNE_FEATURES_tune-armv7athf-neon	?= "${TUNE_FEATURES_tune_armv7at} callconvention-hard"

# Base Big Endian tunes -- some may not exist... match above list
AVAILTUNES += "armv4b armv4tb armv5b armv5tb armv5eb armv5teb armv5b-vfp armv5tb-vfp armv5eb-vfp armv5teb-vfp"
AVAILTUNES += "armv6b armv6tb armv7b armv7tb armv7b-neon armv7tb-neon armv7ab armv7atb armv7ab-neon armv7atb-neon"
TUNE_FEATURES_tune-armv4b		?= "${TUNE_FEATURES_tune-armv4} bigendian"
TUNE_FEATURES_tune-armv4tb		?= "${TUNE_FEATURES_tune-armv4t} bigendian"
TUNE_FEATURES_tune-armv5b		?= "${TUNE_FEATURES_tune-armv5} bigendian"
TUNE_FEATURES_tune-armv5tb		?= "${TUNE_FEATURES_tune-armv5t} bigendian"
TUNE_FEATURES_tune-armv5eb		?= "${TUNE_FEATURES_tune-armv5e} bigendian"
TUNE_FEATURES_tune-armv5teb		?= "${TUNE_FEATURES_tune-armv5te} bigendian"
TUNE_FEATURES_tune-armv5b-vfp		?= "${TUNE_FEATURES_tune-armv5-vfp} bigendian"
TUNE_FEATURES_tune-armv5tb-vfp		?= "${TUNE_FEATURES_tune-armv5t-vfp} bigendian"
TUNE_FEATURES_tune-armv5eb-vfp		?= "${TUNE_FEATURES_tune-armv5e-vfp} bigendian"
TUNE_FEATURES_tune-armv5teb-vfp		?= "${TUNE_FEATURES_tune-armv5te-vfp} bigendian"
TUNE_FEATURES_tune-armv6b		?= "${TUNE_FEATURES_tune-armv6} bigendian"
TUNE_FEATURES_tune-armv6tb		?= "${TUNE_FEATURES_tune-armv6t} bigendian"
TUNE_FEATURES_tune-armv7b		?= "${TUNE_FEATURES_tune-armv7} bigendian"
TUNE_FEATURES_tune-armv7tb		?= "${TUNE_FEATURES_tune-armv7t} bigendian"
TUNE_FEATURES_tune-armv7b-neon		?= "${TUNE_FEATURES_tune-armv7-neon} bigendian"
TUNE_FEATURES_tune-armv7tb-neon		?= "${TUNE_FEATURES_tune-armv7t-neon} bigendian"
TUNE_FEATURES_tune-armv7ab		?= "${TUNE_FEATURES_tune-armv7a} bigendian"
TUNE_FEATURES_tune-armv7atb		?= "${TUNE_FEATURES_tune-armv7at} bigendian"
TUNE_FEATURES_tune-armv7ab-neon		?= "${TUNE_FEATURES_tune-armv7a-neon} bigendian"
TUNE_FEATURES_tune-armv7atb-neon	?= "${TUNE_FEATURES_tune-armv7at-neon} bigendian"

# Big Endian Hardware Floating ABI tunes
# Requires VFP support
AVAILTUNES += "armv5hfb-vfp armv5thfb-vfp armv5ehfb-vfp armv5tehfb-vfp armv6hfb armv6thfb"
AVAILTUNES += "armv7hfb armv7thfb armv7hfb-neon armv7thfb-neon armv7ahfb armv7ahfb-neon armv7athfb-neon"
TUNE_FEATURES_tune-armv5hfb-vfp		?= "${TUNE_FEATURES_tune-armv5b-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv5thfb-vfp	?= "${TUNE_FEATURES_tune-armv5tb-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv5ehfb-vfp	?= "${TUNE_FEATURES_tune-armv5eb-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv5tehfb-vfp	?= "${TUNE_FEATURES_tune-armv5teb-vfp} callconvention-hard"
TUNE_FEATURES_tune-armv6hfb		?= "${TUNE_FEATURES_tune-armv6b} callconvention-hard"
TUNE_FEATURES_tune-armv6thfb		?= "${TUNE_FEATURES_tune-armv6tb} callconvention-hard"
TUNE_FEATURES_tune-armv7hfb		?= "${TUNE_FEATURES_tune-armv7b} callconvention-hard"
TUNE_FEATURES_tune-armv7thfb		?= "${TUNE_FEATURES_tune-armv7tb} callconvention-hard"
TUNE_FEATURES_tune-armv7hfb-neon	?= "${TUNE_FEATURES_tune-armv7b-neon} callconvention-hard"
TUNE_FEATURES_tune-armv7thfb-neon	?= "${TUNE_FEATURES_tune_armv7tb-neon} callconvention-hard"
TUNE_FEATURES_tune-armv7ahfb		?= "${TUNE_FEATURES_tune_armv7ab} callconvention-hard"
TUNE_FEATURES_tune-armv7athfb		?= "${TUNE_FEATURES_tune_armv7atb} callconvention-hard"
TUNE_FEATURES_tune-armv7ahfb-neon	?= "${TUNE_FEATURES_tune_armv7ab} callconvention-hard"
TUNE_FEATURES_tune-armv7athfb-neon	?= "${TUNE_FEATURES_tune_armv7atb} callconvention-hard"

# Select a reasonable default
TUNENAME ?= "armv4"

# Generate the TUNE_ARCH name, and compiler tuning
require conf/machine/include/arm/feature-arm-isa.inc
require conf/machine/include/arm/feature-arm-thumb.inc
require conf/machine/include/arm/feature-arm-abi.inc
require conf/machine/include/arm/feature-arm-fpu.inc

TUNE_ARCH = "${@bb.utils.contains("TUNE_FEATURES", "bigendian", "armeb", "arm", d)}"
TUNE_PKGARCH = "${@(d.getVar('ARM_ARCH', True) or '').replace('-','')}${ARM_THUMB}${ARM_DSP}${ARM_EABI}${ARM_ENDIAN}${ARM_FPU}"

# Little Endian - Soft Float Without Thumb
PACKAGE_EXTRA_ARCHS_tune-armv4 		= "arm armv4"
PACKAGE_EXTRA_ARCHS_tune-armv5 		= "${PACKAGE_EXTRA_ARCHS_tune-armv4} armv5"
PACKAGE_EXTRA_ARCHS_tune-armv5-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5} armv5-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5e 	= "${PACKAGE_EXTRA_ARCHS_tune-armv5} armv5e"
PACKAGE_EXTRA_ARCHS_tune-armv5e-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5-vfp} armv5e armv5e-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6		= "${PACKAGE_EXTRA_ARCHS_tune-armv5e-vfp} armv6-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7		= "${PACKAGE_EXTRA_ARCHS_tune-armv6} armv7-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7a		= "${PACKAGE_EXTRA_ARCHS_tune-armv7} armv7a-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7} armv7-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7a-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7a} armv7a-vfp-neon"

# With Thumb
PACKAGE_EXTRA_ARCHS_tune-armv4t 	= "${PACKAGE_EXTRA_ARCHS_tune-armv4} armv4t"
PACKAGE_EXTRA_ARCHS_tune-armv5t 	= "${PACKAGE_EXTRA_ARCHS_tune-armv4t} armv5 armv5t"
PACKAGE_EXTRA_ARCHS_tune-armv5t-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5t} armv5-vfp armv5t-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5te 	= "${PACKAGE_EXTRA_ARCHS_tune-armv5t} armv5e armv5te"
PACKAGE_EXTRA_ARCHS_tune-armv5te-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5t-vfp} armv5e armv5te armv5e-vfp armv5te-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6t		= "${PACKAGE_EXTRA_ARCHS_tune-armv5te-vfp} armv6-vfp armv6t-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7t		= "${PACKAGE_EXTRA_ARCHS_tune-armv6t} armv7-vfp armv7t2-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7at	= "${PACKAGE_EXTRA_ARCHS_tune-armv7t} armv7a-vfp armv7at2-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7t-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7t} armv7-vfp-neon armv7at2-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7at-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7at} armv7a-vfp-neon armv7at2-vfp-neon"

# Little Endian - Hard Float Without Thumb
PACKAGE_EXTRA_ARCHS_tune-armv5hf-vfp	= "armv5hf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5ehf-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5hf-vfp} armv5ehf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6hf	= "${PACKAGE_EXTRA_ARCHS_tune-armv5ehf-vfp} armv6hf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7hf	= "${PACKAGE_EXTRA_ARCHS_tune-armv6hf} armv7hf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7ahf	= "${PACKAGE_EXTRA_ARCHS_tune-armv7hf} armv7ahf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7hf-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7hf} armv7hf-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7ahf-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7ahf} armv7ahf-vfp-neon"

# With Thumb
PACKAGE_EXTRA_ARCHS_tune-armv5thf-vfp	= "armv5hf-vfp armv5thf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5tehf-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5thf-vfp} armv5ehf-vfp armv5tehf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6thf	= "${PACKAGE_EXTRA_ARCHS_tune-armv5tehf-vfp} armv6hf-vfp armv6thf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7thf	= "${PACKAGE_EXTRA_ARCHS_tune-armv6thf} armv7hf-vfp armv7t2hf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7athf	= "${PACKAGE_EXTRA_ARCHS_tune-armv7thf} armv7ahf-vfp armv7at2hf-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7thf-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7thf} armv7hf-vfp-neon armv7at2hf-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7athf-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7athf} armv7ahf-vfp-neon armv7at2hf-vfp-neon"

# Big Endian - Soft Float Without Thumb
PACKAGE_EXTRA_ARCHS_tune-armv4b 	= "armeb armv4b"
PACKAGE_EXTRA_ARCHS_tune-armv5b 	= "${PACKAGE_EXTRA_ARCHS_tune-armv4} armv5b"
PACKAGE_EXTRA_ARCHS_tune-armv5b-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5} armv5b-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5eb 	= "${PACKAGE_EXTRA_ARCHS_tune-armv5} armv5eb"
PACKAGE_EXTRA_ARCHS_tune-armv5eb-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5-vfp} armv5eb armv5eb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6b		= "${PACKAGE_EXTRA_ARCHS_tune-armv5e-vfp} armv6b-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7b		= "${PACKAGE_EXTRA_ARCHS_tune-armv6} armv7b-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7ab	= "${PACKAGE_EXTRA_ARCHS_tune-armv7} armv7ab-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7b-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7} armv7b-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7ab-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7a} armv7ab-vfp-neon"

# With Thumb
PACKAGE_EXTRA_ARCHS_tune-armv4tb 	= "${PACKAGE_EXTRA_ARCHS_tune-armv4} armv4tb"
PACKAGE_EXTRA_ARCHS_tune-armv5tb 	= "${PACKAGE_EXTRA_ARCHS_tune-armv4t} armv5b armv5tb"
PACKAGE_EXTRA_ARCHS_tune-armv5tb-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5t} armv5b-vfp armv5tb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5teb 	= "${PACKAGE_EXTRA_ARCHS_tune-armv5t} armv5eb armv5teb"
PACKAGE_EXTRA_ARCHS_tune-armv5teb-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5t-vfp} armv5eb armv5teb armv5eb-vfp armv5teb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6tb	= "${PACKAGE_EXTRA_ARCHS_tune-armv5te-vfp} armv6b-vfp armv6tb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7tb	= "${PACKAGE_EXTRA_ARCHS_tune-armv6t} armv7b-vfp armv7t2b-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7atb	= "${PACKAGE_EXTRA_ARCHS_tune-armv7t} armv7ab-vfp armv7at2b-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7tb-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7t} armv7b-vfp-neon armv7at2b-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7atb-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7at} armv7ab-vfp-neon armv7at2b-vfp-neon"

# Big Endian - Hard Float Without Thumb
PACKAGE_EXTRA_ARCHS_tune-armv5hfb-vfp	= "armv5hfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5ehfb-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5hfb-vfp} armv5ehfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6hfb	= "${PACKAGE_EXTRA_ARCHS_tune-armv5ehfb-vfp} armv6hfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7hfb	= "${PACKAGE_EXTRA_ARCHS_tune-armv6hfb} armv7hfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7ahfb	= "${PACKAGE_EXTRA_ARCHS_tune-armv7hfb} armv7ahfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7hfb-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7hfb} armv7hfb-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7ahfb-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7ahfb} armv7ahfb-vfp-neon"

# With Thumb
PACKAGE_EXTRA_ARCHS_tune-armv5thfb-vfp	= "armv5hfb-vfp armv5thfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv5tehfb-vfp	= "${PACKAGE_EXTRA_ARCHS_tune-armv5thfb-vfp} armv5ehfb-vfp armv5tehfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv6thfb	= "${PACKAGE_EXTRA_ARCHS_tune-armv5tehfb-vfp} armv6hfb-vfp armv6thfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7thfb	= "${PACKAGE_EXTRA_ARCHS_tune-armv6thfb} armv7hfb-vfp armv7t2hfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7athfb	= "${PACKAGE_EXTRA_ARCHS_tune-armv7thfb} armv7ahfb-vfp armv7at2hfb-vfp"
PACKAGE_EXTRA_ARCHS_tune-armv7thfb-neon	= "${PACKAGE_EXTRA_ARCHS_tune-armv7thfb} armv7hfb-vfp-neon armv7at2hfb-vfp-neon"
PACKAGE_EXTRA_ARCHS_tune-armv7athfb-neon = "${PACKAGE_EXTRA_ARCHS_tune-armv7athfb} armv7ahfb-vfp-neon armv7at2hfb-vfp-neon"

PACKAGE_EXTRA_ARCHS = "${PACKAGE_EXTRA_ARCHS_tune-${TUNENAME}}"
