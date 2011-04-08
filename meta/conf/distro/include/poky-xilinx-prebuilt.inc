#
# Config to use xilinx prebuilt toolchain
#

TARGET_VENDOR = "-unknown"

#PREFERRED_PROVIDER_linux-libc-headers = "xilinx-prebuilt-toolchain"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}gcc = "xilinx-prebuilt-toolchian"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}gcc-intermediate = "xilinx-prebuilt-toolchain"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}gcc-initial = "xilinx-prebuilt-toolchain"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}binutils = "xilinx-prebuilt-toolchain"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}libc = "xilinx-prebuilt-toolchain"
#PREFERRED_PROVIDER_virtual/libc = "xilinx-prebuilt-toolchain"
#PREFERRED_PROVIDER_virtual/libintl = "xilinx-prebuilt-toolchain"
#PREFERRED_PROVIDER_virtual/libiconv = "xilinx-prebuilt-toolchain"
#PREFERRED_PROVIDER_virtual/linux-libc-headers = "xilinx-prebuilt-toolchain"
