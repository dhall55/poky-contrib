FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

# enable the time limited kernel configuration options
SRC_URI += "file://kvm.cfg" 
PR .= ".1"

