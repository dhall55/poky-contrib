#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Joshua Lock <josh@linux.intel.com>
# Authored by Dongxiao Xu <dongxiao.xu@intel.com>
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
import gobject
import re
from bb.ui.crumbs.hobwidget import HobWidget
from bb.ui.crumbs.detaildialog import DetailDialog

class PackageListModel(gtk.TreeStore):
    """
    This class defines an gtk.TreeStore subclass which will convert the output
    of the bb.event.TargetsTreeGenerated event into a gtk.TreeStore whilst also
    providing convenience functions to access gtk.TreeModel subclasses which
    provide filtered views of the data.
    """
    (COL_PKGNAME, COL_VER, COL_REV, COL_RNM, COL_SEC, COL_SUM, COL_RDEP, COL_RPROV, COL_SIZE, COL_BINB, COL_INC) = range(11)

    __gsignals__ = {
        "packagelist-populated" : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                ()),
        "image-info-updated"    : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                ()),
        }

    """
    """
    def __init__(self):
        self.contents = None
        self.packages = None
        self.images = None
        self.selected_image = None
        self.image_size = 0
        
        gtk.TreeStore.__init__ (self,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_BOOLEAN)

    """
    Helper function to determine whether an item is a package
    """
    def package_model_filter(self, model, it):
        name = model.get_value(it, self.COL_PKGNAME)
        return True

    """
    Create, if required, and return a filtered gtk.TreeModel
    """
    def packages_model(self):
        if not self.packages:
            self.packages = self.filter_new()
            self.packages.set_visible_func(self.package_model_filter)
        return self.packages

    def populate_recipe(self, recipe):
        pniter = self.append(None)
        self.set(pniter, self.COL_PKGNAME, recipe,
                         self.COL_INC, False)
        return pniter

    """
    The populate() function takes as input the data from a
    bb.event.TargetsTreeGenerated event and populates the TaskList.
    Once the population is done it emits gsignal packagelist-populated
    to notify any listeners that the model is ready
    """
    def populate(self, pniter, pkginfo):
        pkg = pkginfo['pkg']
        pkgv = pkginfo['pkgv']
        pkgr = pkginfo['pkgr']
        pkg_rename = pkginfo['pkg_rename']
        section = pkginfo['section']
        summary = pkginfo['summary']
        rdep = pkginfo['rdep']
        rrec = pkginfo['rrec']
        rprov = pkginfo['rprov']
        if len(pkginfo['size']) > 3:
            size = '%.1f' % (int(pkginfo['size'])*1.0/1024) + ' MB'
        else:
            size = pkginfo['size'] + ' KB'

        if pkginfo['size'] == "0" and not pkginfo['allow_empty']:
            return

        self.set(self.append(pniter), self.COL_PKGNAME, pkg, self.COL_VER, pkgv,
                 self.COL_REV, pkgr, self.COL_RNM, pkg_rename,
                 self.COL_SEC, section, self.COL_SUM, summary,
                 self.COL_RDEP, rdep + ' ' + rrec, self.COL_RPROV, rprov,
                 self.COL_SIZE, size, self.COL_BINB, "", self.COL_INC, False)

    def map_pn_path(self):
        self.pn_path = {}
        it = self.get_iter_first()
        while it:
            child_it = self.iter_children(it)
            while child_it:
                pn = self.get_value(child_it, self.COL_PKGNAME)
                path = self.get_path(child_it)
                self.pn_path[pn] = path
                child_it = self.iter_next(child_it)
            it = self.iter_next(it)

    """
    Check whether the item at item_path is included or not
    """
    def contents_includes_path(self, item_path):
        return self[item_path][self.COL_INC]

    """
    Update the image size
    incr == True, add a certain package into image
    incr == False, remove a certain package from image
    """
    def update_image_size(self, str_size, incr):
        if not str_size:
            return

        unit = str_size.split()
        if unit[1] == 'MB':
            size = float(unit[0])*1024
        else:
            size = float(unit[0])

        if incr:
            self.image_size += size
        else:
            self.image_size -= size

        if self.image_size < 1:
            self.image_size = 0

        self.emit("image-info-updated")

    """
    Mark a certain package as selected.
    All its dependencies are marked as selected.
    The recipe provides the package is marked as selected.
    If user explicitly selects a recipe, all its providing packages are selected
    """
    def include_item(self, item_path, binb="", image_contents=False):
        if self[item_path][self.COL_INC]:
            return

        item_name = self[item_path][self.COL_PKGNAME]
        item_rdep = self[item_path][self.COL_RDEP]

        self[item_path][self.COL_INC] = True

        self.update_image_size(self[item_path][self.COL_SIZE], True)

        it = self.get_iter(item_path)

        # If user explicitly selects a recipe, all its providing packages are selected.
        if not self[item_path][self.COL_VER] and binb == "User Selected":
            child_it = self.iter_children(it)
            while child_it:
                child_path = self.get_path(child_it)
                child_included = self[child_path][self.COL_INC]
                if not child_included:
                    self.include_item(child_path, binb="User Selected", image_contents=False)
                child_it = self.iter_next(child_it)
            return

        # The recipe provides the package is also marked as selected
        parent_it = self.iter_parent(it)
        if parent_it:
            parent_path = self.get_path(parent_it)
            self[parent_path][self.COL_INC] = True

        item_bin = self[item_path][self.COL_BINB].split(', ')
        if binb and not binb in item_bin:
            item_bin.append(binb)
            self[item_path][self.COL_BINB] = ', '.join(item_bin).lstrip(', ')

        if item_rdep:
            # Ensure all of the items deps are included and, where appropriate,
            # add this item to their COL_BINB
            for dep in item_rdep.split(" "):
                if dep.startswith('('):
                    continue
                # If the contents model doesn't already contain dep, add it
                dep_path = self.find_path_for_item(dep)
                if not dep_path:
                    continue
                dep_included = self.contents_includes_path(dep_path)

                if dep_included and not dep in item_bin:
                    # don't set the COL_BINB to this item if the target is an
                    # item in our own COL_BINB
                    dep_bin = self[dep_path][self.COL_BINB].split(', ')
                    if not item_name in dep_bin:
                        dep_bin.append(item_name)
                        self[dep_path][self.COL_BINB] = ', '.join(dep_bin).lstrip(', ')
                elif not dep_included:
                    self.include_item(dep_path, binb=item_name, image_contents=False)

    """
    Mark a certain package as de-selected.
    All other packages that depends on this package are marked as de-selected.
    If none of the packages provided by the recipe, the recipe should be marked as de-selected.
    If user explicitly de-select a recipe, all its providing packages are de-selected.
    """
    def exclude_item(self, item_path):
        if not self[item_path][self.COL_INC]:
            return

        self[item_path][self.COL_INC] = False

        self.update_image_size(self[item_path][self.COL_SIZE], False)

        item_name = self[item_path][self.COL_PKGNAME]
        item_rdep = self[item_path][self.COL_RDEP]
        it = self.get_iter(item_path)

        # If user explicitly de-select a recipe, all its providing packages are de-selected.
        if not self[item_path][self.COL_VER]:
            child_it = self.iter_children(it)
            while child_it:
                child_path = self.get_path(child_it)
                child_included = self[child_path][self.COL_INC]
                if child_included:
                    self.exclude_item(child_path)
                child_it = self.iter_next(child_it)
            return

        # If none of the packages provided by the recipe, the recipe should be marked as de-selected.
        parent_it = self.iter_parent(it)
        peer_iter = self.iter_children(parent_it)
        enabled = 0
        while peer_iter:
            peer_path = self.get_path(peer_iter)
            if self[peer_path][self.COL_INC]:
                enabled = 1
                break
            peer_iter = self.iter_next(peer_iter)
        if not enabled:
            parent_path = self.get_path(parent_it)
            self[parent_path][self.COL_INC] = False

        # All packages that depends on this package are de-selected.
        if item_rdep:
            for dep in item_rdep.split(" "):
                if dep.startswith('('):
                    continue
                dep_path = self.find_path_for_item(dep)
                if not dep_path:
                    continue
                dep_bin = self[dep_path][self.COL_BINB].split(', ')
                if item_name in dep_bin:
                    dep_bin.remove(item_name)
                    self[dep_path][self.COL_BINB] = ', '.join(dep_bin).lstrip(', ')

        item_bin = self[item_path][self.COL_BINB].split(', ')
        if item_bin:
            for binb in item_bin:
                binb_path = self.find_path_for_item(binb)
                if not binb_path:
                    continue
                self.exclude_item(binb_path)

    """
    Find the model path for the item_name
    Returns the path in the model or None
    """
    def find_path_for_item(self, item_name):
        if item_name not in self.pn_path.keys():
            return None
        else:
            return self.pn_path[item_name]

    def set_selected_packages(self, packagelist):
        for pn in packagelist:
            if pn in self.pn_path.keys():
                path = self.pn_path[pn]
                self.include_item(item_path=path,
                                  binb="User Selected")
        self.emit("image-info-updated")

    def get_selected_packages(self):
        it = self.get_iter_first()
        packagelist = []

        while it:
            child_it = self.iter_children(it)
            while child_it:
                if self.get_value(child_it, self.COL_INC):
                    name = self.get_value(child_it, self.COL_PKGNAME)
                    packagelist.append(name)
                child_it = self.iter_next(child_it)
            it = self.iter_next(it)

        return packagelist

    """
    Empty self.contents by setting the include of each entry to None
    """
    def reset(self):
        self.image_size = 0
        it = self.get_iter_first()
        while it:
            self.set(it, self.COL_INC, False)
            child_it = self.iter_children(it)
            while child_it:
                self.set(child_it,
                         self.COL_INC, False,
                         self.COL_BINB, "")
                child_it = self.iter_next(child_it)
            it = self.iter_next(it)
        self.emit("image-info-updated")

class PackageSelection (gtk.Window):
    def __init__(self, packagemodel, handler):
        gtk.Window.__init__(self)
        self.package_model = packagemodel
        self.selected_packages = []
        self.last_selected_packages = []

    def update_image_info(self, model):
        size = model.image_size
        str_size = str(int(size))
        self.selected_packages = self.package_model.get_selected_packages()
        pkgnum = len(self.selected_packages)
        if len(str_size) > 3:
            size_label = '%.1f' % (size*1.0/1024) + ' MB'
        else:
            size_label = str(size) + ' KB'
        self.expand.set_label("Selected %s (%s) packages" % (pkgnum, size_label))
        self.add_selected_packages(self.package_model, self.package_buffer)

    def save_last_selected_packages(self):
        self.last_selected_packages = self.selected_packages[:len(self.selected_packages)]

    def clear_last_selected_packages(self):
        self.last_selected_packages = []

    def update_package_model(self):
        # We want the packages model to be alphabetised and sortable so create
        # a TreeModelSort to use in the view
        packagesaz_model = gtk.TreeModelSort(self.package_model.packages_model())
        packagesaz_model.set_sort_column_id(self.package_model.COL_PKGNAME, gtk.SORT_ASCENDING)
        # Unset default sort func so that we only toggle between A-Z and
        # Z-A sorting
        packagesaz_model.set_default_sort_func(None)
        self.packagesaz_tree.set_model(packagesaz_model)
        self.packagesaz_tree.expand_all()

        if self.selected_packages:
            self.package_model.set_selected_packages(self.selected_packages)

        self.update_image_info(self.package_model)

    def recipesaz_cell2_toggled_cb(self, cell, path, tree):
        self.save_last_selected_packages()
        HobWidget.toggle_selection_include_cb(cell, path, self, tree, self.package_model)

    def packagesaz(self):
        vbox = gtk.VBox(False, 6)
        vbox.show()
        self.packagesaz_tree = gtk.TreeView()
        self.packagesaz_tree.set_headers_visible(True)
        self.packagesaz_tree.set_headers_clickable(True)
        self.packagesaz_tree.set_enable_search(True)
        self.packagesaz_tree.set_search_column(0)
        self.packagesaz_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('Package')
        col.set_clickable(True)
        col.set_sort_column_id(self.package_model.COL_PKGNAME)
        col.set_resizable(True)
        col.set_min_width(100)
        col.set_max_width(300)
        col1 = gtk.TreeViewColumn('Size')
        col1.set_resizable(True)
        col1.set_clickable(True)
        col1.set_min_width(100)
        col1.set_max_width(200)
        col2 = gtk.TreeViewColumn('Included')
        col2.set_min_width(50)
        col2.set_max_width(100)
        col2.set_sort_column_id(self.package_model.COL_INC)

        self.packagesaz_tree.append_column(col)
        self.packagesaz_tree.append_column(col1)
        self.packagesaz_tree.append_column(col2)

        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererToggle()
        cell2.set_property('activatable', True)
        cell2.connect("toggled", self.recipesaz_cell2_toggled_cb, self.packagesaz_tree)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_end(cell2, True)

        col.set_attributes(cell, text=self.package_model.COL_PKGNAME)
        col1.set_attributes(cell1, text=self.package_model.COL_SIZE)
        col2.set_attributes(cell2, active=self.package_model.COL_INC)

        self.packagesaz_tree.show()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.packagesaz_tree)
        vbox.pack_start(scroll, True, True, 0)

        hb = gtk.HBox(False, 10)
        hb.show()
        self.search = gtk.Entry()
        self.search.show()
        self.packagesaz_tree.set_search_entry(self.search)
        hb.pack_end(self.search, False, False, 0)
        label = gtk.Label("Search:")
        label.show()
        hb.pack_end(label, False, False, 6)

        button = gtk.Button("Reset")
        button.connect('clicked', self.reset_clicked_cb)
        hb.pack_start(button, False, False, 0)

        vbox.pack_start(hb, False, False, 0)

        return vbox

    def reset_clicked_cb(self, tbutton):
        self.selected_packages = None
        self.package_model.reset()
        self.clear_last_selected_packages()

    def show_binb_info(self, model, path, parent):
        it = model.get_iter(path)
        binb = model.get_value(it, model.COL_BINB)
        w = DetailDialog(title="", content="Brought in by: " + binb, parent=self)
        w.show()
        del w

    def selection_clicked_cb(self, textview, event, model):
        if event.type != gtk.gdk.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False
        package_buffer = textview.get_buffer()
        x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
        it = textview.get_iter_at_location(x, y)

        tags = it.get_tags()
        for tag in tags:
            path = tag.get_data("path")
            if path != 0:
                window = textview.get_toplevel()
                self.show_binb_info(model, path, window)
                break

        return False

    def insert_text_with_tag(self, package_buffer, it, text, path, highlight=False):
        if highlight:
            tag = package_buffer.create_tag(None, foreground="blue", background="yellow")
        else:
            tag = package_buffer.create_tag(None, foreground="blue")
        tag.set_data("path", path)
        package_buffer.insert_with_tags(it, text, tag)

    def add_selected_packages(self, model, package_buffer):
        package_buffer.set_text("")
        it = model.get_iter_first()
        while it:
            child_it = model.iter_children(it)
            while child_it:
                name = model.get_value(child_it, model.COL_PKGNAME)
                inc = model.get_value(child_it, model.COL_INC)
                path = model.get_path(child_it)
                if inc:
                    tit = package_buffer.get_end_iter()
                    if name in self.last_selected_packages:
                        self.insert_text_with_tag(package_buffer, tit, name + "  ", path)
                    else:
                        self.insert_text_with_tag(package_buffer, tit, name + "  ", path, True)
                child_it = model.iter_next(child_it)
            it = model.iter_next(it)

    def motion_cb(self, textview, event):
        x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
        it = textview.get_iter_at_location(x, y)
        if it.get_tags():
            textview.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
        else:
            textview.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))

    def selections(self):
        vbox = gtk.VBox(False, 5)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        vbox.add(scroll)

        self.expand = gtk.Expander("Selected Packages")
        self.expand.set_expanded(True)
        scroll.add_with_viewport(self.expand)

        tv = gtk.TextView()
        tv.set_editable(False)
        tv.set_wrap_mode(gtk.WRAP_WORD)
        tv.set_cursor_visible(False)
        self.package_buffer = gtk.TextBuffer()
        tv.set_buffer(self.package_buffer)
        tv.connect("event-after", self.selection_clicked_cb, self.package_model)
        tv.connect("motion-notify-event", self.motion_cb)
        self.expand.add(tv)

        return vbox


    def main(self, button):
        window = gtk.Dialog("Package List", None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        window.set_size_request(800, 600)
        window.set_border_width(5)

        table = gtk.Table(10, 10, True)
        table.set_col_spacings(3)
        window.vbox.add(table)

        ins = gtk.Notebook()
        ins.set_show_tabs(True)
        label = gtk.Label("Packages")
        ins.append_page(self.packagesaz(), tab_label=label)
        ins.set_current_page(0)

        table.attach(ins, 0, 7, 0, 10, gtk.FILL | gtk.EXPAND, gtk.FILL | gtk.EXPAND, 1, 1)

        selections = self.selections()
        table.attach(selections, 7, 10, 0, 10, gtk.FILL | gtk.EXPAND, gtk.FILL | gtk.EXPAND, 1, 1)        

        self.update_package_model()

        window.show_all()
        id = self.package_model.connect("image-info-updated", self.update_image_info)
        response = window.run()
        self.package_model.disconnect(id)
        window.destroy()
