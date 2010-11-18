S = "${WORKDIR}/linux"

# Determine which branch to fetch and build. Not all branches are in the
# upstream repo (but will be locally created after the fetchers run) so 
# a fallback branch needs to be chosen. 
#
# The default machine 'UNDEFINED'. If the machine is not set to a specific
# branch in this recipe or in a recipe extension, then we fallback to a 
# branch that is always present 'standard'. This sets the KBRANCH variable
# and is used in the SRC_URI. The machine is then set back to ${MACHINE},
# since futher processing will use that to create local branches
python __anonymous () {
    import bb, re

    bb.data.setVar("KBRANCH", "${KMACHINE}-${LINUX_KERNEL_TYPE}", d)
    mach = bb.data.getVar("KMACHINE", d, 1)
    if mach == "UNDEFINED":
        bb.data.setVar("KBRANCH", "standard", d)
        bb.data.setVar("KMACHINE", "${MACHINE}", d)
        bb.data.setVar("SRCREV_machine", "standard", d)
        bb.data.setVar("BOOTSTRAP", "t", d)
}

do_patch() {
	cd ${S}
	if [ -f ${WORKDIR}/defconfig ]; then
	    defconfig=${WORKDIR}/defconfig
	fi

	# simply ensures that a branch of the right name has been created
	createme ${ARCH} ${KMACHINE}-${LINUX_KERNEL_TYPE} ${defconfig}
	if [ $? -ne 0 ]; then
		echo "ERROR. Could not create ${KMACHINE}-${LINUX_KERNEL_TYPE}"
		exit 1
	fi

        # updates or generates the target description
	if [ -n "${KERNEL_FEATURES}" ]; then
	       addon_features="--features ${KERNEL_FEATURES}"
	fi
	updateme ${addon_features} ${ARCH} ${WORKDIR}
	if [ $? -ne 0 ]; then
		echo "ERROR. Could not update ${KMACHINE}-${LINUX_KERNEL_TYPE}"
		exit 1
	fi

	# executes and modifies the source tree as required
	patchme ${KMACHINE}-${LINUX_KERNEL_TYPE}
	if [ $? -ne 0 ]; then
		echo "ERROR. Could not modify ${KMACHINE}-${LINUX_KERNEL_TYPE}"
		exit 1
	fi
}
         

do_kernel_checkout() {
	if [ -d ${WORKDIR}/.git/refs/remotes/origin ]; then
		echo "Fixing up git directory for ${KMACHINE}-${LINUX_KERNEL_TYPE}"
		rm -rf ${S}
		mkdir ${S}
		mv ${WORKDIR}/.git ${S}
	
		if [ -e ${S}/.git/packed-refs ]; then
			cd ${S}
			rm -f .git/refs/remotes/origin/HEAD
IFS='
';

			for r in `git show-ref | grep remotes`; do
				ref=`echo $r | cut -d' ' -f1`; 
				b=`echo $r | cut -d'/' -f4`;
				echo $ref > .git/refs/heads/$b
			done
			cd ..
		else
			mv ${S}/.git/refs/remotes/origin/* ${S}/.git/refs/heads
			rmdir ${S}/.git/refs/remotes/origin
		fi
	fi
	cd ${S}

	# checkout and clobber and unimportant files
	git checkout -f ${KBRANCH}
}
do_kernel_checkout[dirs] = "${S}"

addtask kernel_checkout before do_patch after do_unpack

do_kernel_configme() {
	echo "Doing kernel configme"

	cd ${S}
	configme --reconfig
	if [ $? -ne 0 ]; then
		echo "ERROR. Could not configure ${KMACHINE}-${LINUX_KERNEL_TYPE}"
		exit 1
	fi

	echo "# CONFIG_WRNOTE is not set" >> ${B}/.config
	echo "# Global settings from linux recipe" >> ${B}/.config
	echo "CONFIG_LOCALVERSION="\"${LINUX_VERSION_EXTENSION}\" >> ${B}/.config
}

do_kernel_configcheck() {
	echo "[INFO] validating kernel configuration"
	cd ${B}/..
	kconf_check ${B}/.config ${B} ${S} ${B} ${LINUX_VERSION} ${KMACHINE}-${LINUX_KERNEL_TYPE}
}

