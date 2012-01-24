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

def base_branches():
    branches = [ "yocto/standard/base",
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
