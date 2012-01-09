#
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
from bb.ui.crumbs.hobcolors import HobColors

class DetailDialog(gtk.Dialog):
    """
    A dialog widget to show "brought in by" info when a recipe/package is clicked.
    """

    def __init__(self, title, content, parent=None):
        gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, None)

        self.set_position(gtk.WIN_POS_MOUSE)
        self.set_resizable(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(HobColors.DARK))

        hbox = gtk.HBox(False, 0)
        self.vbox.pack_start(hbox, expand=False, fill=False, padding=10)

        label = gtk.Label(content)
        label.set_alignment(0, 0)
        label.set_line_wrap(True)
        label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(HobColors.WHITE))

        hbox.pack_start(label, expand=False, fill=False, padding=10)

    def show(self):
        self.show_all()
        response = self.run()
        self.destroy()

