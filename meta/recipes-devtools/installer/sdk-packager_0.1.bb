# sdk packager bb file
#
# Copyright 2011 by SecretLab Technologies.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.


DESCRIPTION = "Meta package for creating sdk tarball"
LIC_FILES_CHKSUM = "file://${POKYBASE}/LICENSE;md5=3f40d7994397109285ec7b81fdeb3b58 \
                    file://${POKYBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"
LICENSE = "MIT"

ALLOW_EMPTY = "1"

PR = "r0"
inherit populate_sdk deploy
CONFIG_SITE := "${@siteinfo_get_files(d)}"

fakeroot do_deploy () {
# create tar ball
DEPLOY_DIR_PKG="${DEPLOY_DIR}/ipk"
if [ -d ${DEPLOY_DIR_PKG} ]; then
	cd ${DEPLOY_DIR_PKG}
	tar cfj  poky-pkgs-${SDK_VERSION}-${SDK_ARCH}-nativesdk.tar.bz2 ${SDK_ARCH}-nativesdk
fi
}

do_patch[noexec] = "1"
do_install[noexec] = "1"
do_configure[noexec] = "1"
do_compile[noexec] = "1"
do_package[noexec] = "1"
do_package_write[noexec] = "1"
do_package_write_ipk[noexec] = "1"
do_package_write_rpm[noexec] = "1"
do_package_write_deb[noexec] = "1"
do_poplulate_sysroot[noexec] = "1"

addtask deploy before do_populate_sysroot after do_unpack
