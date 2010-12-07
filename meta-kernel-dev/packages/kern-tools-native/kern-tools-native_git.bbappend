# if working on kernel tools, point this at your local repo

SRCREV=${AUTOREV}
BB_LOCALCOUNT_OVERRIDE = "1"
LOCALCOUNT = "0"

# ksrc ?= /path/to/wr-kernel-tools
# SRC_URI = "git://${ksrc}"
