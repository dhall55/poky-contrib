# BitBake Graphical GTK User Interface
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

import gtk
from bb.ui.crumbs.runningbuild import Colors

class HobProgressBar (gtk.ProgressBar):
    def __init__(self):
        gtk.ProgressBar.__init__(self)
        self.set_style(True)
        self.percentage = 0

    def set_style(self, status):
        rcstyle = gtk.RcStyle()
        rcstyle.fg[2] = gtk.gdk.Color(0, 0, 0)
        if status:
            rcstyle.bg[3] = gtk.gdk.Color(Colors.RUNNING)
        else:
            rcstyle.bg[3] = gtk.gdk.Color(Colors.ERROR)
        self.modify_style(rcstyle)
        self.set_size_request(1000, 35)

    def set_title(self, text=None):
        if not text:
            text = ""
        text += " %.0f%%" % self.percentage
        gtk.ProgressBar.set_text(self, text)

    def reset(self):
        gtk.ProgressBar.set_fraction(self, 0)
        self.set_text("")
        self.set_style(True)
        self.percentage = 0

    def update(self, current, total=None):
        #show the progress bar if 0%
        if (current == 0) or (total == None) or (total == 0):
            gtk.ProgressBar.show(self)
            gtk.ProgressBar.set_fraction(self, 0)
        else:
            gtk.ProgressBar.set_fraction(self, current*1.0/total)
            self.percentage = int(current*100.0/total)
            if self.percentage > 100:
                self.percentage = 100

# A Case would be a possibility, for example,
#     weight_matrix = [[0.2, 0.3], [0.15, 0.35]]
#     event_indexes = { "ParseStarted"                 : 0,
#                       "ParseProgress"                : 0,
#                       "ParseCompleted"               : 0,
#                       "TreeDataPreparationStarted"   : 1,
#                       "TreeDataPreparationProgress"  : 1,
#                       "TreeDataPreparationCompleted" : 1,
#                }
#     step_indexes = {  FAST_IMAGE_GENERATING          : 0,
#                       IMAGE_GENERATING               : 1,
#                }
# where indexes indidate:
# event ParseXXX happens before event TreeDataPreparationXXX
# step FAST_IMAGE_GENERATING happens before step IMAGE_GENERATING;
# the row number of weight_matrix is the index of a step
# the col number of weight_matrix is the index of an event
# so, weight_matrix is a matrix of S(num of steps) X E(num of events);
# weight for event ParseXXXes during step FAST_IMAGE_GENERATING is weight_matrix[0][0] = 0.2 while
# weight for event TreeDataPreparationXXXes during step IMAGE_GENERATING is weight_matrix[1][1] = 0.35
# and so on.
class Case:
    def __init__(self, weight_matrix):
        self.event_indexes = {}
        self.step_indexes = {}
        self.eindex = 0
        self.sindex = 0
        if weight_matrix:
            self.weight_matrix = weight_matrix
        else:
            self.weight_matrix = [[1.0]]

    def append_event(self, names):
        # names is a tuple
        # e.g. append_event(("ParseStarted", "ParseProgress", "ParseCompleted"))
        # check
        if (not names) or (not self.weight_matrix):
            return
        if not (self.eindex < len(self.weight_matrix[0])):
            return

        for name in names:
            if not self.has_event(name):
                self.event_indexes[name] = self.eindex
        self.eindex += 1

    def append_step(self, stepid):
        # stepid an enumeration type
        # e.g. append_step(FAST_IMAGE_GENERATING)
        # check
        if (not stepid) or (not self.weight_matrix):
            return
        if not (self.sindex < len(self.weight_matrix)):
            return

        if not self.step_indexes.has_key(stepid):
            self.step_indexes[stepid] = self.sindex
        self.sindex += 1

    def has_event(self, name):
        return self.event_indexes.has_key(name)

# A ComplexHobProgressBar is composed of a set of Cases
class ComplexHobProgressBar(HobProgressBar):
    def __init__(self):
        HobProgressBar.__init__(self)
        self.num_of_cases = 0
        self.cases = []   #self.cases is the list of cases
        self.case = None
        self.stepid = None # the current stepid of self.case
        self.title_header = ""

    def add_case(self, case):
        if case:
            self.cases.append(case)
            self.num_of_cases += 1

    def set_case_by_num(self, cur):
        if cur < self.num_of_cases:
            self.case = self.cases[cur]
        else:
            self.case = None

    def set_stepid(self, stepid, title_header=None):
        if not stepid:
            return
        self.stepid = stepid
        if title_header:
            self.title_header = title_header

    def set_title(self, text=None):
        if not text:
            text = ""
        HobProgressBar.set_title(self, self.title_header + text)

    def update(self, current, total=None, eventname=None):
        # check
        if not self.case or not self.stepid: #the current case(possibility) and the current stepid is not speicified
            return
        if not self.case.has_event(eventname):
            return
        if not self.case.step_indexes.has_key(self.stepid):
            return

        eindex = self.case.event_indexes[eventname]
        sindex = self.case.step_indexes[self.stepid]

        if (current == 0) or (total == None) or (total == 0):
            mixed_fraction = 0
        else:
            mixed_fraction = self.case.weight_matrix[sindex][eindex]*current*1.0/total

        for i in range(0, sindex):
            for j in range(0, len(self.case.weight_matrix[i])):
                mixed_fraction += self.case.weight_matrix[i][j]

        for i in range(0, eindex):
            mixed_fraction += self.case.weight_matrix[sindex][i]
        gtk.ProgressBar.set_fraction(self, mixed_fraction)

        self.percentage = int(mixed_fraction*100)
        if self.percentage > 100:
            self.percentage = 100
