FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

COMPATIBLE_MACHINE_{{=machine}} = "{{=machine}}"
{{ input type:"choicelist" name:"kmachine" gen:"bsp.kernel.base_branches" msg:"Please choose a machine branch to base this BSP on =>" }}
KMACHINE_{{=machine}}  = "{{=kmachine}}"

{{ input type:"boolean" name:"smp" msg:"Do you need SMP support?" }}
{{ if smp == "yes": }}
KERNEL_FEATURES_append_{{=machine}} += " cfg/smp.scc"

YOCTO_KERNEL_EXTERNAL_BRANCH_{{=machine}}  = "{{=kmachine}}"

SRC_URI += "file://{{=machine}}-standard.scc \
            file://{{=machine}}.scc \
            file://{{=machine}}.cfg \
            file://{{=machine}}-preempt-rt.scc \
           "

{{ input type:"checklist" name:"kfeatures" gen:"bsp.kernel.features" msg:"Please choose the kernel features to use in this BSP (select one or more e.g. 1 3 5) =>" }}
{{ for kfeature in kfeatures: }}
KERNEL_FEATURES_append_{{=machine}} += " {{=kfeature}}"

#SRCREV_machine_pn-linux-yocto_{{=machine}} ?= "153cb7313697f6638109ed6ce40009af353eeb94"
#SRCREV_meta_pn-linux-yocto_{{=machine}} ?= "67ce7623909cef63927fd145026aaf371cf4abf1"
