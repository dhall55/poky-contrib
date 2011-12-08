IMAGE_FEATURES += "apps-console-core dev-pkgs ssh-server-openssh"

IMAGE_INSTALL = "\
    ${OE_BASE_INSTALL} \
    task-core-basic \
    task-core-lsb \
    "

inherit core-image
