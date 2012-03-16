SRC_URI += "file://crosscompile.patch"

# Misc build failure for master HEAD
SRC_URI += "file://fix_open_max_preprocessor_error.patch"

PR = "r0"

SRC_URI[md5sum] = "3a3c4281f32c8702749e8f129372a355"
SRC_URI[sha256sum] = "280a14c5de8697a4aab18dca85429671286e69e5ada0c1535f03666e56f07799"
