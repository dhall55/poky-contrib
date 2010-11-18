inherit kernel
require linux-yocto.inc

# Set this to 'preempt_rt' in the local.conf if you want a real time kernel
PV = "2.6.34+git${SRCPV}"
SRCREV_FORMAT = "meta_machine"


python __anonymous () {
    import bb, re

    rev = bb.data.getVar("SRCREV_machine", d, 1)
    if rev == "standard":
        bb.data.setVar("SRCREV_machine", "${SRCREV_meta}", d)
}

# To use a staged, on-disk bare clone of a Wind River Kernel, use a 
# variant of the below
# SRC_URI = "git://///path/to/kernel/default_kernel.git;fullclone=1"
SRC_URI = "git://git.pokylinux.org/linux-2.6-windriver.git;protocol=git;fullclone=1;branch=${KBRANCH};name=machine \
           git://git.pokylinux.org/linux-2.6-windriver.git;protocol=git;noclone=1;branch=wrs_meta;name=meta"

LINUX_VERSION ?= "v2.6.34"
LINUX_VERSION_EXTENSION ?= "-yocto-${LINUX_KERNEL_TYPE}"
PR = "r14"

# functionality flags
KERNEL_REVISION_CHECKING ?= "t"
KERNEL_FEATURES=features/netfilter

do_validate_branches() {
	cd ${S}
 	branch_head=`git show-ref -s --heads ${KBRANCH}`
 	meta_head=`git show-ref -s --heads wrs_meta`
 	target_branch_head="${SRCREV_machine}"
 	target_meta_head="${SRCREV_meta}"

	# nothing to do if bootstrapping
 	if [ -n "${BOOTSTRAP}" ]; then
 	 	return
 	fi

	if [ -n "$target_branch_head" ] && [ "$branch_head" != "$target_branch_head" ]; then
		if [ -n "${KERNEL_REVISION_CHECKING}" ]; then
			git show ${target_branch_head} > /dev/null 2>&1
			if [ $? -eq 0 ]; then
				echo "Forcing branch ${KMACHINE}-${LINUX_KERNEL_TYPE} to ${target_branch_head}"
				git branch -m ${KMACHINE}-${LINUX_KERNEL_TYPE} ${KMACHINE}-${LINUX_KERNEL_TYPE}-orig
				git checkout -b ${KMACHINE}-${LINUX_KERNEL_TYPE} ${target_branch_head}
			else
				echo "ERROR ${target_branch_head} is not a valid commit ID."
				echo "The kernel source tree may be out of sync"
				exit 1
			fi	       
		fi
	fi

	if [ "$meta_head" != "$target_meta_head" ]; then
		if [ -n "${KERNEL_REVISION_CHECKING}" ]; then
			git show ${target_meta_head} > /dev/null 2>&1
			if [ $? -eq 0 ]; then
				echo "Forcing branch wrs_meta to ${target_meta_head}"
				git branch -m wrs_meta wrs_meta-orig
				git checkout -b wrs_meta ${target_meta_head}
			else
				echo "ERROR ${target_meta_head} is not a valid commit ID"
				echo "The kernel source tree may be out of sync"
				exit 1
			fi	   
		fi
	fi

	# restore the branch for builds
	git checkout -f ${KBRANCH}
}

do_kernel_link_vmlinux() {
	if [ ! -d "${B}/arch/${ARCH}/boot" ]; then
		mkdir ${B}/arch/${ARCH}/boot
	fi
	cd ${B}/arch/${ARCH}/boot
	ln -sf ../../../vmlinux
}
addtask kernel_link_vmlinux after do_compile before do_install
addtask validate_branches before do_patch after do_kernel_checkout

require perf.inc
