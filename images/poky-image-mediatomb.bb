#
# Copyright (C) 2010 Intel Corporation.
#
require recipes-core/images/poky-image-minimal.bb

IMAGE_INSTALL += "dropbear mediatomb task-poky-nfs-server"

LICENSE = "MIT"
