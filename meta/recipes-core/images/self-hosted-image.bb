IMAGE_INSTALL = "task-core-boot task-core-apps-console task-core-ssh-openssh task-self-hosted"

OE_EXTRA_INSTALL = "\
    task-self-hosted \
    "

inherit core-image

PR = "r1"
