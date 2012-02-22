# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# Copyright 2012 Intel Corporation
# Authored-by:  Tom Zanussi <tom.zanussi@intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import os
import shutil
from tags import *


def find_bblayers(scripts_path):
    """
    Find and return a sanitized list of the layers found in BBLAYERS.
    """
    bblayers_conf = os.path.join(scripts_path, "../build/conf/bblayers.conf")
    f = open(bblayers_conf, "r")
    lines = f.readlines()
    layers = []
    for line in lines:
        line = line.strip()
        in_bblayers = False
        if line.startswith("BBLAYERS"):
            in_bblayers = True
        # todo: currently we expect each layer on its own line
        # and we won't even pick up any dir in the first line
        if line.startswith("/"):
            if line.endswith("\\"):
                line = line[:-1].strip()
            layers.append(line)
    return layers


def find_bsp_layer(scripts_path, machine):
    """
    Find and return a machine's BSP layer in BBLAYERS.
    """
    layers = find_bblayers(scripts_path)
    for layer in layers:
        # todo: for now we only find the correct layer
        # if it has the machine name in the layer dir
        # i.e. we don't look inside the layer dir for
        # the machine name yet
        if machine in layer:
            return layer

    print "Unable to find the BSP layer for machine %s." % machine
    print "Please make sure it is listed in bblayers.conf"
    sys.exit(1)


def gen_choices_str(choices):
    """
    Generate a numbered list of choices from a list of choices for
    display to the user.
    """
    choices_str = ""
    for i, choice in enumerate(choices):
        choices_str += "\t" + str(i + 1) + ") " + choice + "\n"
    return choices_str


def read_config_items(scripts_path, machine):
    """
    Find and return a list of config items (CONFIG_XXX) in a machine's
    top-level config fragment [machine.cfg]
    """
    layer = find_bsp_layer(scripts_path, machine)
    machine_cfg = os.path.join(layer, "recipes-kernel/linux/linux-yocto")
    machine_cfg = os.path.join(machine_cfg, "%s.cfg" % machine)
    f = open(machine_cfg, "r")
    lines = f.readlines()
    config_items = []
    for line in lines:
        s = line.strip()
        if s:
            config_items.append(s)
    return config_items


def write_config_items(scripts_path, machine, config_items):
    """
    Write (replace) the list of config items (CONFIG_XXX) in a
    machine's top-level config fragment [machine.cfg]
    """
    layer = find_bsp_layer(scripts_path, machine)
    machine_cfg = os.path.join(layer, "recipes-kernel/linux/linux-yocto")
    machine_cfg = os.path.join(machine_cfg, "%s.cfg" % machine)
    f = open(machine_cfg, "w")
    for item in config_items:
        f.write(item + "\n")
    f.close()


def yocto_kernel_config_list(scripts_path, machine):
    """
    Display the list of config items (CONFIG_XXX) in a machine's
    top-level config fragment [machine.cfg]
    """
    config_items = read_config_items(scripts_path, machine)
    print "The current set of machine-specific kernel config items for %s is:" % machine
    print gen_choices_str(config_items)


def map_choice(choice_str, array):
    """
    Match the text of a choice with a list of choices, returning the
    index of the match, or -1 if not found.
    """
    for i, item in enumerate(array):
        if choice_str == array[i]:
            return i
    return -1


def yocto_kernel_config_rm(scripts_path, machine):
    """
    Display the list of config items (CONFIG_XXX) in a machine's
    top-level config fragment [machine.cfg], prompt the user for one
    or more to remove, and remove them.
    """
    config_items = read_config_items(scripts_path, machine)
    print "Specify the kernel config items to remove:"
    input = raw_input(gen_choices_str(config_items))
    rm_choices = input.split()
    rm_choices.sort()
    removed = []
    for choice in reversed(rm_choices):
        idx = int(choice) - 1
        if idx < 0 or idx >= len(config_items):
            print "Invalid choice (%d), exiting" % idx
            sys.exit(1)
        removed.append(config_items.pop(idx))
    write_config_items(scripts_path, machine, config_items)
    print "Removed items:"
    for r in removed:
        print "\t%s" % r


def yocto_kernel_config_add(scripts_path, machine, config_items):
    """
    Add one or more config items (CONFIG_XXX) to a machine's top-level
    config fragment [machine.cfg].
    """
    new_items = []
    for item in config_items:
        if not item.startswith("CONFIG") or (not "=y" in item and not "=m" in item):
            print "Invalid config item (%s), exiting" % item
            sys.exit(1)
        new_items.append(item)

    cur_items = read_config_items(scripts_path, machine)
    cur_items.extend(new_items)
    write_config_items(scripts_path, machine, cur_items)
    print "Added items:"
    for n in new_items:
        print "\t%s" % n


def find_bsp_kernel_src_uri(scripts_path, machine, start_end_only = False):
    """
    Parse the SRC_URI append in the kernel .bbappend, returing a list
    of individual components, and the start/end positions of the
    SRC_URI statement, so it can be regenerated in the same position.
    If start_end_only is True, don't return the list of elements, only
    the start and end positions.

    Returns (SRC_URI start line, SRC_URI end_line, list of split
    SRC_URI items).

    If no SRC_URI, start line = -1.

    todo: need to handle multiple SRC_URI +=
    todo: clean up/simplify
    """
    layer = find_bsp_layer(scripts_path, machine)
    kernel_bbappend = os.path.join(layer,
                                   "recipes-kernel/linux/linux-yocto_3.0.bbappend")

    f = open(kernel_bbappend, "r")
    src_uri_line = ""
    in_src_uri = False
    lines = f.readlines()
    first_line = last_line = -1
    quote_start = quote_end = -1
    for n, line in enumerate(lines):
        line = line.strip()
        if line.startswith("SRC_URI"):
            first_line = n
            in_src_uri = True
        if in_src_uri:
            src_uri_line += line
            if quote_start == -1:
                idx = line.find("\"")
                if idx != -1:
                    quote_start = idx + 1
            idx = line.find("\"", quote_start)
            quote_start = 0 # set to 0 for all but first line
            if idx != -1:
                quote_end = idx
                last_line = n
                break

    if first_line == -1: # no SRC_URI, which is fine too
        return (-1, -1, None)
    if quote_start == -1:
        print "Bad kernel SRC_URI (missing opening quote), exiting."
        sys.exit(1)
    if quote_end == -1:
        print "Bad SRC_URI (missing closing quote), exiting."
        sys.exit(1)
    if start_end_only:
        return (first_line, last_line, None)

    idx = src_uri_line.find("\"")
    src_uri_line = src_uri_line[idx + 1:]
    idx = src_uri_line.find("\"")
    src_uri_line = src_uri_line[:idx]

    src_uri = src_uri_line.split()
    for i, item in enumerate(src_uri):
        idx = item.find("\\")
        if idx != -1:
            src_uri[i] = item[idx + 1:]

    if not src_uri[len(src_uri) - 1]:
        src_uri.pop()

    for i, item in enumerate(src_uri):
        idx = item.find(SRC_URI_FILE)
        if idx == -1:
            print "Bad SRC_URI (invalid item, %s), exiting." % item
            sys.exit(1)
        src_uri[i] = item[idx + len(SRC_URI_FILE):]

    return (first_line, last_line, src_uri)     


def find_patches(src_uri):
    """
    Filter out the top-level patches from the SRC_URI.
    """
    patches = []
    for item in src_uri:
        # anything in a subdir is a feature
        if item.endswith(".patch") and "/" not in item:
            patches.append(item)
    return patches


def yocto_kernel_patch_list(scripts_path, machine):
    """
    Display the list of top-level patches for a machine.
    """
    (start_line, end_line, src_uri) = find_bsp_kernel_src_uri(scripts_path, machine)
    patches = find_patches(src_uri)

    print "The current set of machine-specific patches for %s is:" % machine
    print gen_choices_str(patches)


def write_uri_lines(ofile, src_uri):
    """
    Write URI elements to output file ofile.
    """
    ofile.write("SRC_URI += \" \\\n")
    for item in src_uri:
        ofile.write("\t%s%s \\\n" % (SRC_URI_FILE, item))
    ofile.write("\t\"\n")


def write_kernel_src_uri(scripts_path, machine, src_uri):
    """
    Write (replace) the SRC_URI append for a machine from a list
    SRC_URI elements.
    """
    layer = find_bsp_layer(scripts_path, machine)
    kernel_bbappend = os.path.join(layer,
                                   "recipes-kernel/linux/linux-yocto_3.0.bbappend")

    (uri_start_line, uri_end_line, unused) = find_bsp_kernel_src_uri(scripts_path, machine, True)

    kernel_bbappend_prev = kernel_bbappend + ".prev"
    shutil.copyfile(kernel_bbappend, kernel_bbappend_prev)
    ifile = open(kernel_bbappend_prev, "r")
    ofile = open(kernel_bbappend, "w")
    ifile_lines = ifile.readlines()
    if uri_start_line == -1:
        uri_end_line = len(ifile_lines) # make sure we add at end
    wrote_src_uri = False
    for i, ifile_line in enumerate(ifile_lines):
        if i < uri_start_line:
            ofile.write(ifile_line)
        elif i > uri_end_line:
            ofile.write(ifile_line)
        else:
            if not wrote_src_uri:
                write_uri_lines(ofile, src_uri)
                wrote_src_uri = True
    if uri_start_line == -1:
        write_uri_lines(ofile, src_uri)


def yocto_kernel_patch_add(scripts_path, machine, patches):
    """
    Add one or more patches to a machine's top-level set of patches.
    """
    layer = find_bsp_layer(scripts_path, machine)
    src_uri_dir = os.path.join(layer, "recipes-kernel/linux/linux-yocto")

    new_patches = []
    for patch in patches:
        if not os.path.isfile(patch):
            print "Couldn't find patch (%s), exiting" % patch
            sys.exit(1)
        basename = os.path.basename(patch)
        src_uri_patch = os.path.join(src_uri_dir, basename)
        shutil.copyfile(patch, src_uri_patch)
        new_patches.append(basename)

    (unused, unused, src_uri) = find_bsp_kernel_src_uri(scripts_path, machine)
    src_uri.extend(new_patches)
    write_kernel_src_uri(scripts_path, machine, src_uri)

    print "Added patches:"
    for n in new_patches:
        print "\t%s" % n


def yocto_kernel_patch_rm(scripts_path, machine):
    """
    Remove one or more patches from a machine's top-level set of patches.
    """
    (start_line, end_line, src_uri) = find_bsp_kernel_src_uri(scripts_path, machine)
    patches = find_patches(src_uri)

    layer = find_bsp_layer(scripts_path, machine)
    src_uri_dir = os.path.join(layer, "recipes-kernel/linux/linux-yocto")

    print "Specify the patches to remove:"
    input = raw_input(gen_choices_str(patches))
    rm_choices = input.split()
    rm_choices.sort()
    removed = []
    for choice in reversed(rm_choices):
        idx = int(choice) - 1
        if idx < 0 or idx >= len(patches):
            print "Invalid choice (%d), exiting" % idx
            sys.exit(1)
        idx = map_choice(patches[idx], src_uri)
        removed.append(src_uri.pop(idx))

    write_kernel_src_uri(scripts_path, machine, src_uri)

    print "Removed patches:"
    for r in removed:
        src_uri_patch = os.path.join(src_uri_dir, r)
        os.remove(src_uri_patch)
        print "\t%s" % r


def base_branches():
    branches = [ "yocto/standard",
                 "yocto/standard/common-pc",
                 "yocto/standard/common-pc-64",]
    return branches


def features():
    features = [ "features/debugfs",
                 "features/drm-emgd",
                 "features/ftrace",
                 "features/ericsson-3g",
                 "features/intel-e1xxxx",
                 "features/taskstats",
                 "features/yaffs2",]
    return features


