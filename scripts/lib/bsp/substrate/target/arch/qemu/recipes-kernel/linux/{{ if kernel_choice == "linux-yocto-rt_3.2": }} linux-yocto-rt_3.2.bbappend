FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

PR := "${PR}.1"

COMPATIBLE_MACHINE_{{=machine}} = "{{=machine}}"
{{ input type:"boolean" name:"new_kbranch_linux_yocto_rt_3_2" prio:"20" msg:"Do you need a new machine branch for this BSP (the alternative is to re-use an existing branch)? [Y/n]" default:"y" }}
{{ input type:"choicelist" name:"base_kbranch_linux_yocto_rt_3_2" gen:"bsp.kernel.all_branches" prio:"20" msg:"Please choose a machine branch to base this BSP on =>" depends-on:"new_kbranch_linux_yocto_rt_3_2" depends-on-val:"y" default:"standard/preempt-rt" }}
{{ input type:"choicelist" name:"existing_kbranch_linux_yocto_rt_3_2" gen:"bsp.kernel.all_branches" prio:"20" msg:"Please choose a machine branch to base this BSP on =>" depends-on:"new_kbranch_linux_yocto_rt_3_2" depends-on-val:"n" default:"standard/preempt-rt/base" }}

{{ if new_kbranch_linux_yocto_rt_3_2 == "y": }}
KBRANCH_{{=machine}}  = "{{=base_kbranch_linux_yocto_rt_3_2}}/{{=machine}}"
{{ if new_kbranch_linux_yocto_rt_3_2 == "n": }}
KBRANCH_{{=machine}}  = "{{=existing_kbranch_linux_yocto_rt_3_2}}"

{{ if new_kbranch_linux_yocto_rt_3_2 == "y": }}
YOCTO_KERNEL_EXTERNAL_BRANCH_{{=machine}}  = "{{=base_kbranch_linux_yocto_rt_3_2}}/{{=machine}}"

KMACHINE_{{=machine}}  = "{{=machine}}"

{{ input type:"boolean" name:"smp_linux_yocto_rt_3_2" prio:"30" msg:"Do you need SMP support? (Y/n)" default:"y"}}
{{ if smp_linux_yocto_rt_3_2 == "y": }}
KERNEL_FEATURES_append_{{=machine}} += " cfg/smp.scc"

SRC_URI += "file://{{=machine}}-preempt-rt.scc \
            file://{{=machine}}.scc \
            file://{{=machine}}.cfg \
           "

# uncomment and replace these SRCREVs with the real commit ids once you've had
# the appropriate changes committed to the upstream linux-yocto repo
#SRCREV_machine_pn-linux-yocto-rt_{{=machine}} ?= "417fc778a86e81303bab5883b919ee422ec51c04"
#SRCREV_meta_pn-linux-yocto-rt_{{=machine}} ?= "138bf5b502607fe40315c0d76822318d77d97e01"
