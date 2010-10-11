#
# Copyright (C) 2010 Intel Corporation.
#

# Extending minimal results in build failure regardless of which
# path I use to poky-image-minimal.bb. Ideally this file would
# contain only the following two lines.
#require "poky-image-minimal.bb"
#IMAGE_INSTALL += "dropbear mediatomb"

# Since the above doesn't work, duplicate minimal and add the
# two packages.
IMAGE_INSTALL = "task-poky-boot ${ROOTFS_PKGMANAGE} dropbear mediatomb"

IMAGE_LINGUAS = " "

LICENSE = "MIT"

inherit poky-image

# remove not needed ipkg informations
ROOTFS_POSTPROCESS_COMMAND += "remove_packaging_data_files ; "

