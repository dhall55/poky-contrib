DESCRIPTION = "For us to know and for you to wonder ..."
LICENSE = "MIT"

LIC_FILES_CHKSUM = "file://${THISDIR}/../../COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

PR = "r1"

inherit core-image

IMAGE_FEATURES =+ "package-management \
		  "

IMAGE_INSTALL += "rygel-plugin-media-export \
                  guacamayo-session-mediaserver \
                  tzdata                     \
                  dconf                      \
                  guacamayo-gsettings        \
                  dbus                       \
                  dbus-x11                   \
                 "

GUACA_DEMOS_FEATURE = "${@base_contains("IMAGE_FEATURES", "guacamayo-demos", "guacamayo-demos-audio guacamayo-demos-video guacamayo-demos-pictures", "", d)}"

IMAGE_INSTALL += "${GUACA_DEMOS_FEATURE}"
