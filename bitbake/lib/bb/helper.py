#
# Helper for BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Shane Wang <shane.wang@intel.com>
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

import os

class CpuInfo(object):

    coefficient = 4

    @classmethod
    def getNumOfCpus(cls):
        pfile = os.popen('cat /proc/cpuinfo | grep cpu\ cores')
        num = len(pfile.readlines())
        return num

    @classmethod
    def getNumOfCpuCores(cls):
        pfile = os.popen('cat /proc/cpuinfo | grep cpu\ cores | cut -d: -f2')
        contents = pfile.readlines()
        num = int(contents[0])
        return num

