DESCRIPTION = "An image you can use to monitor the yocto-autobuilder. Requires meta-oe, meta-gnome and meta-browsers"
IMAGE_FEATURES += "firefox splash package-management x11-base x11-sato ssh-server-dropbear"
inherit core-image
IMAGE_INSTALL += "firefox packagegroup-core-x11-sato-games"
PR = "r2"

fakeroot do_populate_lavalamp () {
	echo '#!/bin/sh'  >> ${IMAGE_ROOTFS}/etc/profile.d/firefox.sh
	echo 'firefox "autobuilder.yoctoproject.org:8010/grid?reload=5"' >> ${IMAGE_ROOTFS}/etc/profile.d/firefox.sh
	chmod 755 ${IMAGE_ROOTFS}/etc/profile.d/firefox.sh
	echo 'export http_proxy="http://proxy.jf.intel.com:911/"' >> ${IMAGE_ROOTFS}/etc/profile
	echo 'export https_proxy="https://proxy.jf.intel.com:911/"' >> ${IMAGE_ROOTFS}/etc/profile
	echo 'export ftp_proxy="http://proxy.jf.intel.com:911/"' >> ${IMAGE_ROOTFS}/etc/profile
	echo 'export no_proxy=".intel.com"' >> ${IMAGE_ROOTFS}/etc/profile
}

IMAGE_PREPROCESS_COMMAND += "do_populate_lavalamp; "

