FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"
COMPATIBLE_MACHINE_foo = "foo"
KMACHINE_foo  = "foo"

YOCTO_KERNEL_EXTERNAL_BRANCH_foo  = "yocto/standard/preempt-rt/foo"

SRC_URI += "file://foo-standard.scc \
            file://foo.scc \
            file://foo.cfg \
            file://foo-preempt-rt.scc \
           "

# Update the following to use a different BSP branch or meta SRCREV
#KBRANCH_foo  = "yocto/standard/preempt-rt/base"
#SRCREV_machine_pn-linux-yocto-rt_fo ?= XXXX
#SRCREV_meta_pn-linux-yocto-rt_foo ?= XXXX
