#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Joshua Lock <josh@linux.intel.com>
# Authored by Dongxiao Xu <dongxiao.xu@intel.com>
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

import glib
import gobject
import gtk
from bb.ui.crumbs2.recipelistmodel import RecipeListModel
from bb.ui.crumbs2.hobeventhandler import HobHandler
from bb.ui.crumbs2.hig import CrumbsDialog
import xmlrpclib
import logging
import Queue
import copy

class MainWindow (gtk.Window):

    def __init__(self, recipemodel, handler, layers, mach, pclass, distro, bbthread, pmake, dldir, sstatedir, sstatemirror):
        gtk.Window.__init__(self)
        # global state
        self.layers = layers.split()
        self.layers_default = copy.copy(self.layers)
        self.curr_mach = mach
        self.machine_handler_id = None
        self.curr_distro = distro
        self.distro_handler_id = None
        self.curr_package_format = pclass
        self.package_handler_id = None
        self.bbthread = bbthread
        self.pmake = pmake
        self.dldir = dldir
        self.sstatedir = sstatedir
        self.sstatemirror = sstatemirror
        self.image_combo_id = None
        self.generating = False
        self.selected_image = None
        self.selected_recipes = None

        self.recipe_model = recipemodel
        self.recipe_model.connect("recipelist-populated", self.update_recipe_model)
        self.recipe_model.connect("image-changed", self.image_changed_string_cb)

        self.handler = handler

        self.connect("delete-event", self.destroy_window)
        self.set_title("HOB")
        self.set_icon_name("applications-development")
        self.set_default_size(1000, 650)

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(0)
        vbox.show()
        self.add(vbox)
        configview = self.create_config_gui()
        recipeview = self.create_recipe_gui()
        self.nb = gtk.Notebook()
        self.nb.append_page(configview)
        self.nb.append_page(recipeview)
        self.nb.set_current_page(0)
        self.nb.set_show_tabs(False)
        vbox.pack_start(self.nb, expand=True, fill=True)

    def load_current_layers(self, data):
        for layer in self.layers:
            self.layer_store.append([layer])

    def conf_error(self, lbl):
        dialog = CrumbsDialog(self, lbl)
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        response = dialog.run()
        dialog.destroy()

    def add_layer_cb(self, action):
        dialog = gtk.FileChooserDialog("Add new layer", self,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        label = gtk.Label("Select the layer you wish to add")
        label.show()
        dialog.set_extra_widget(label)
        response = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()

        lbl = "<b>Error</b>\nUnable to load layer <i>%s</i> because " % path
        if response == gtk.RESPONSE_YES:
            # FIXME: verify we've actually got a layer conf?
            import os
            import os.path
            if not path:
                lbl += "it is an invalid path."
            elif not os.path.exists(path+"/conf/layer.conf"):
                lbl += "there is no layer.conf inside the directory."
            elif path in self.layers:
                lbl += "it is already in loaded layers."
            else:
                self.layer_store.append([path])
                self.layers.append(path)
                self.handler.layer_refresh(self.layers)
                return
            self.conf_error(lbl)

    def del_layer_cb(self, action):
        model, iter = self.ltv.get_selection().get_selected()
        lbl = "<b>Error</b>\nUnable to remove default layers <i>%s</i>" % self.layers_default
        if iter:
            layer = model.get_value(iter, 0)
            if layer in self.layers_default:
                self.conf_error(lbl)
            else:
                self.layer_store.remove(iter)
                self.layers.remove(layer)
                self.handler.layer_refresh(self.layers)

    def update_machines(self, handler, machines):
        active = 0
        # disconnect the signal handler before updating the combo model
        if self.machine_handler_id:
            self.machine_combo.disconnect(self.machine_handler_id)
            self.machine_handler_id = None

        model = self.machine_combo.get_model()
        if model:
            model.clear()

        for machine in machines:
            self.machine_combo.append_text(machine)
            if machine == self.curr_mach:
                self.machine_combo.set_active(active)
            active = active + 1

    def update_package_formats(self, handler, formats):
        active = 0
        # disconnect the signal handler before updating the model
        if self.package_handler_id:
            self.package_combo.disconnect(self.package_handler_id)
            self.package_handler_id = None

        model = self.package_combo.get_model()
        if model:
            model.clear()

        for format in formats:
            self.package_combo.append_text(format)
            if format == self.curr_package_format:
                self.package_combo.set_active(active)
            active = active + 1

    def update_distros(self, handler, distros):
        active = 0
        # disconnect the signal handler before updating combo model
        if self.distro_handler_id:
            self.distro_combo.disconnect(self.distro_handler_id)
            self.distro_handler_id = None

        model = self.distro_combo.get_model()
        if model:
            model.clear()

        for distro in distros:
            self.distro_combo.append_text(distro)
            if distro == self.curr_distro:
                self.distro_combo.set_active(active)
            active = active + 1

    def select_dldir_cb(self, action):
        dialog = gtk.FileChooserDialog("Select Download Directory", None,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            path = dialog.get_filename()
            self.dldir_text.set_text(path)

        dialog.destroy()

    def select_sstatedir_cb(self, action):
        dialog = gtk.FileChooserDialog("Select Sstate Directory", None,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            path = dialog.get_filename()
            self.sstatedir_text.set_text(path)

        dialog.destroy()

    def set_busy_cursor(self, busy=True):
        """
        Convenience method to set the cursor to a spinner when executing
        a potentially lengthy process.
        A busy value of False will set the cursor back to the default
        left pointer.
        """
        if busy:
            cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        else:
            # TODO: presumably the default cursor is different on RTL
            # systems. Can we determine the default cursor? Or at least
            # the cursor which is set before we change it?
            cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
        window = self.get_root_window()
        window.set_cursor(cursor)

    def busy_idle_func(self):
        if self.generating:
            self.progress.pulse()
            return True
        else:
            if not self.image_combo_id:
                self.image_combo_id = self.image_combo.connect("changed", self.image_changed_cb)
            self.progress.set_text("Loaded")
            self.progress.set_fraction(0.0)
            self.set_busy_cursor(False)
            return False
    def busy(self, handler):
        self.generating = True
        self.progress.set_text("Loading...")
        self.set_busy_cursor()
        if self.image_combo_id:
            self.image_combo.disconnect(self.image_combo_id)
            self.image_combo_id = None
        self.progress.pulse()
        gobject.timeout_add (100, self.busy_idle_func)
        self.disable_widgets()

    def data_generated(self, handler):
        self.generating = False
        self.enable_widgets()

    def enable_widgets(self):
        self.nb.set_sensitive(True)

    def disable_widgets(self):
        self.nb.set_sensitive(False)

    def config_next_clicked_cb(self, button):
        self.nb.set_current_page(1)
    
        self.handler.init_cooker()
        self.handler.set_bblayers(self.layers)
        self.handler.set_machine(self.machine_combo.get_active_text())
        self.handler.set_package_format(self.package_combo.get_active_text())
        self.handler.set_distro(self.distro_combo.get_active_text())
        self.handler.set_dl_dir(self.dldir_text.get_text())
        self.handler.set_sstate_dir(self.sstatedir_text.get_text())
        self.handler.set_sstate_mirror(self.sstatemirror_text.get_text())
        self.handler.set_pmake(self.pmake_spinner.get_value_as_int())
        self.handler.set_bbthreads(self.bb_spinner.get_value_as_int())

        self.handler.generate_data()

    def update_recipe_model(self, model):
        # We want the recipes model to be alphabetised and sortable so create
        # a TreeModelSort to use in the view
        recipesaz_model = gtk.TreeModelSort(self.recipe_model.recipes_model())
        recipesaz_model.set_sort_column_id(self.recipe_model.COL_NAME, gtk.SORT_ASCENDING)
        # Unset default sort func so that we only toggle between A-Z and
        # Z-A sorting
        recipesaz_model.set_default_sort_func(None)
        self.recipesaz_tree.set_model(recipesaz_model)

        self.image_combo.set_model(self.recipe_model.images_model())
        self.image_combo.set_active(-1)

        if not self.image_combo_id:
            self.image_combo_id = self.image_combo.connect("changed", self.image_changed_cb)

        # We want the contents to be alphabetised so create a TreeModelSort to
        # use in the view
        contents_model = gtk.TreeModelSort(self.recipe_model.contents_model())
        contents_model.set_sort_column_id(self.recipe_model.COL_NAME, gtk.SORT_ASCENDING)
        # Unset default sort func so that we only toggle between A-Z and
        # Z-A sorting
        contents_model.set_default_sort_func(None)
        self.contents_tree.set_model(contents_model)
        self.tasks_tree.set_model(self.recipe_model.tasks_model())

        if self.selected_image:
            if self.image_combo_id:
                self.image_combo.disconnect(self.image_combo_id)
                self.image_combo_id = None
            self.recipe_model.set_selected_image(self.selected_image)
            if not self.image_combo_id:
                self.image_combo_id = self.image_combo.connect("changed", self.image_changed_cb)

        if self.selected_recipes:
            self.recipe_model.set_selected_recipes(self.selected_recipes)

    def image_changed_string_cb(self, model, new_image):
        self.selected_image = new_image
        # disconnect the image combo's signal handler
        if self.image_combo_id:
            self.image_combo.disconnect(self.image_combo_id)
            self.image_combo_id = None
        cnt = 0
        it = self.recipe_model.images.get_iter_first()
        while it:
            path = self.recipe_model.images.get_path(it)
            if self.recipe_model.images[path][self.recipe_model.COL_NAME] == new_image:
                self.image_combo.set_active(cnt)
                break
            it = self.recipe_model.images.iter_next(it)
            cnt = cnt + 1
        # Reconnect the signal handler
        if not self.image_combo_id:
            self.image_combo_id = self.image_combo.connect("changed", self.image_changed_cb)

    def image_changed_cb(self, combo):
        model = self.image_combo.get_model()
        it = self.image_combo.get_active_iter()
        if it:
            path = model.get_path(it)
            # Firstly, deselect the previous image
            userp, _ = self.recipe_model.get_selected_recipes()
            self.recipe_model.reset()
            # Now select the new image and save its path in case we
            # change the image later
            self.toggle_item(path, model, self.recipe_model, image=True)
            if len(userp):
                self.recipe_model.set_selected_recipes(userp)
            self.selected_image = model[path][self.recipe_model.COL_NAME]

    def toggle_item_idle_cb(self, model, listmodel, opath, image):
        """
        As the operations which we're calling on the model can take
        a significant amount of time (in the order of seconds) during which
        the GUI is unresponsive as the main loop is blocked perform them in
        an idle function which at least enables us to set the busy cursor
        before the UI is blocked giving the appearance of being responsive.
        """
        # Whether the item is currently included
        inc = listmodel[opath][listmodel.COL_INC]
        if not inc:
            listmodel.include_item(item_path=opath,
                                   binb="User Selected",
                                   image_contents=image)

        self.set_busy_cursor(False)
        return False

    def toggle_item(self, path, model, listmodel, image=False):
        inc = listmodel[path][listmodel.COL_INC]
        if inc:
            return
        self.set_busy_cursor()
        # Convert path to path in original model
        opath = model.convert_path_to_child_path(path)
        # This is a potentially length call which can block the
        # main loop, therefore do the work in an idle func to keep
        # the UI responsive
        glib.idle_add(self.toggle_item_idle_cb, model, listmodel, opath, image)

        self.dirty = True

    def toggle_include_cb(self, cell, path, tv, listmodel):
        model = tv.get_model()
        self.toggle_item(path, model, listmodel)

    def toggle_selection_include_cb(self, cell, path, tv, listmodel):
        # there's an extra layer of models in the recipes case.
        sort_model = tv.get_model()
        cpath = sort_model.convert_path_to_child_path(path)
        self.toggle_item(cpath, sort_model.get_model(), listmodel)

    def recipesaz(self):
        vbox = gtk.VBox(False, 6)
        vbox.show()
        self.recipesaz_tree = gtk.TreeView()
        self.recipesaz_tree.set_headers_visible(True)
        self.recipesaz_tree.set_headers_clickable(True)
        self.recipesaz_tree.set_enable_search(True)
        self.recipesaz_tree.set_search_column(0)
        self.recipesaz_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('Recipe')
        col.set_clickable(True)
        col.set_sort_column_id(self.recipe_model.COL_NAME)
        col.set_min_width(220)
        col1 = gtk.TreeViewColumn('Description')
        col1.set_resizable(True)
        col1.set_min_width(360)
        col2 = gtk.TreeViewColumn('License')
        col2.set_resizable(True)
        col2.set_clickable(True)
        col2.set_sort_column_id(self.recipe_model.COL_LIC)
        col2.set_min_width(170)
        col3 = gtk.TreeViewColumn('Group')
        col3.set_clickable(True)
        col3.set_sort_column_id(self.recipe_model.COL_GROUP)
        col4 = gtk.TreeViewColumn('Included')
        col4.set_min_width(80)
        col4.set_max_width(90)
        col4.set_sort_column_id(self.recipe_model.COL_INC)

        self.recipesaz_tree.append_column(col)
        self.recipesaz_tree.append_column(col1)
        self.recipesaz_tree.append_column(col2)
        self.recipesaz_tree.append_column(col3)
        self.recipesaz_tree.append_column(col4)
        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell1.set_property('width-chars', 20)
        cell2 = gtk.CellRendererText()
        cell2.set_property('width-chars', 20)
        cell3 = gtk.CellRendererText()
        cell4 = gtk.CellRendererToggle()
        cell4.set_property('activatable', True)
        cell4.connect("toggled", self.toggle_selection_include_cb, self.recipesaz_tree, self.recipe_model)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_start(cell2, True)
        col3.pack_start(cell3, True)
        col4.pack_end(cell4, True)

        col.set_attributes(cell, text=self.recipe_model.COL_NAME)
        col1.set_attributes(cell1, text=self.recipe_model.COL_DESC)
        col2.set_attributes(cell2, text=self.recipe_model.COL_LIC)
        col3.set_attributes(cell3, text=self.recipe_model.COL_GROUP)
        col4.set_attributes(cell4, active=self.recipe_model.COL_INC)

        self.recipesaz_tree.show()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.recipesaz_tree)
        vbox.pack_start(scroll, True, True, 0)

        hb = gtk.HBox(False, 0)
        hb.show()
        self.search = gtk.Entry()
        self.search.set_icon_from_stock(gtk.ENTRY_ICON_SECONDARY, "gtk-clear")
        self.search.connect("icon-release", self.search_entry_clear_cb)
        self.search.show()
        self.recipesaz_tree.set_search_entry(self.search)
        hb.pack_end(self.search, False, False, 0)
        label = gtk.Label("Search Recipes:")
        label.show()
        hb.pack_end(label, False, False, 6)
        vbox.pack_start(hb, False, False, 0)

        return vbox

    def search_entry_clear_cb(self, entry, icon_pos, event):
        entry.set_text("")

    def tasks(self):
        vbox = gtk.VBox(False, 6)
        vbox.show()
        self.tasks_tree = gtk.TreeView()
        self.tasks_tree.set_headers_visible(True)
        self.tasks_tree.set_headers_clickable(False)
        self.tasks_tree.set_enable_search(True)
        self.tasks_tree.set_search_column(0)
        self.tasks_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('Recipe Collection')
        col.set_min_width(430)
        col1 = gtk.TreeViewColumn('Description')
        col1.set_min_width(430)
        col2 = gtk.TreeViewColumn('Include')
        col2.set_min_width(70)
        col2.set_max_width(80)

        self.tasks_tree.append_column(col)
        self.tasks_tree.append_column(col1)
        self.tasks_tree.append_column(col2)

        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererToggle()
        cell2.set_property('activatable', True)
        cell2.connect("toggled", self.toggle_include_cb, self.tasks_tree, self.recipe_model)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_end(cell2, True)

        col.set_attributes(cell, text=self.recipe_model.COL_NAME)
        col1.set_attributes(cell1, text=self.recipe_model.COL_DESC)
        col2.set_attributes(cell2, active=self.recipe_model.COL_INC)

        self.tasks_tree.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.tasks_tree)
        vbox.pack_start(scroll, True, True, 0)

        hb = gtk.HBox(False, 0)
        hb.show()
        search = gtk.Entry()
        search.show()
        self.tasks_tree.set_search_entry(search)
        hb.pack_end(search, False, False, 0)
        label = gtk.Label("Search collections:")
        label.show()
        hb.pack_end(label, False, False, 6)
        vbox.pack_start(hb, False, False, 0)

        return vbox

    def contents(self):
        self.contents_tree = gtk.TreeView()
        self.contents_tree.set_headers_visible(True)
        self.contents_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        # allow searching in the recipe column
        self.contents_tree.set_search_column(0)
        self.contents_tree.set_enable_search(True)

        col = gtk.TreeViewColumn('Recipe')
        col.set_sort_column_id(0)
        col.set_min_width(430)
        col1 = gtk.TreeViewColumn('Brought in by')
        col1.set_resizable(True)
        col1.set_min_width(430)

        self.contents_tree.append_column(col)
        self.contents_tree.append_column(col1)

        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell1.set_property('width-chars', 20)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)

        col.set_attributes(cell, text=self.recipe_model.COL_NAME)
        col1.set_attributes(cell1, text=self.recipe_model.COL_BINB)

        self.contents_tree.show()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.contents_tree)

        return scroll

    def recipe_previous_clicked_cb(self, button):
        self.nb.set_current_page(0)

    def recipe_next_clicked_cb(self, button):
        return
        

    def destroy_window(self, widget, event):
        gtk.main_quit()

    def create_config_gui(self):
        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(5)
        vbox.show()

        table = gtk.Table(10, 5, False)
        table.show()
        vbox.pack_start(table, expand=False, fill=False)

        label = gtk.Label("Layers:")
        label.show()
        table.attach(label, 1, 2, 0, 2)

        self.layer_store = gtk.ListStore(gobject.TYPE_STRING)

        self.ltv = gtk.TreeView()
        self.ltv.set_model(self.layer_store)
        self.ltv.set_headers_visible(False)
        self.ltv.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col0= gtk.TreeViewColumn('Path')
        self.ltv.append_column(col0)

        cell0 = gtk.CellRendererText()
        col0.pack_start(cell0, True)
        col0.set_attributes(cell0, text=0)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.ltv)

        table.attach(scroll, 2, 3, 0, 2)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_MENU)
        add_button = gtk.Button()
        add_button.set_image(image)
        add_button.connect("clicked", self.add_layer_cb)
        table.attach(add_button, 3, 4, 0, 1)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_REMOVE,gtk.ICON_SIZE_MENU)
        del_button = gtk.Button()
        del_button.set_image(image)
        del_button.connect("clicked", self.del_layer_cb)
        table.attach(del_button, 3, 4, 1, 2)
        label = gtk.Label("Machine:")
        label.show()
        table.attach(label, 1, 2, 2, 3)

        self.machine_combo = gtk.combo_box_new_text()
        self.machine_combo.show()
        self.machine_combo.set_tooltip_text("Selects the architecture of the target board for which you would like to build an image.")
        table.attach(self.machine_combo, 2, 4, 2, 3)

        label = gtk.Label("Packaging:")
        label.show()
        table.attach(label, 1, 2, 3, 4)

        self.package_combo = gtk.combo_box_new_text()
        self.package_combo.show()
        table.attach(self.package_combo, 2, 4, 3, 4)

        label = gtk.Label("Distro:")
        label.show()
        table.attach(label, 1, 2, 4, 5)

        self.distro_combo = gtk.combo_box_new_text()
        self.distro_combo.set_tooltip_text("Select the Yocto distribution you would like to use")
        self.distro_combo.show()
        table.attach(self.distro_combo, 2, 4, 4, 5)

        label = gtk.Label("DL_DIR:")
        label.show()
        table.attach(label, 1, 2, 5, 6)

        self.dldir_text = gtk.Entry()
        self.dldir_text.set_text(self.dldir or "")
        self.dldir_text.show()
        table.attach(self.dldir_text, 2, 3, 5, 6)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_MENU)
        open_button = gtk.Button()
        open_button.set_image(image)
        open_button.connect("clicked", self.select_dldir_cb)
        table.attach(open_button, 3, 4, 5, 6)


        label = gtk.Label("SSTATE_DIR:")
        label.show()
        table.attach(label, 1, 2, 6, 7)

        self.sstatedir_text = gtk.Entry()
        self.sstatedir_text.set_text(self.sstatedir or "")
        self.sstatedir_text.show()
        table.attach(self.sstatedir_text, 2, 3, 6, 7)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_MENU)
        open_button = gtk.Button()
        open_button.set_image(image)
        open_button.connect("clicked", self.select_sstatedir_cb)
        table.attach(open_button, 3, 4, 6, 7)

        label = gtk.Label("SSTATE_MIRROR:")
        label.show()
        table.attach(label, 1, 2, 7, 8)

        self.sstatemirror_text = gtk.Entry()
        self.sstatemirror_text.set_text(self.sstatemirror or "")
        self.sstatemirror_text.show()
        table.attach(self.sstatemirror_text, 2, 4, 7, 8)

        label = gtk.Label("BB_NUMBER_THREADS:")
        label.show()
        table.attach(label, 1, 2, 8, 9)
        bb_adjust = gtk.Adjustment(value=self.bbthread, lower=1, upper=16, step_incr=1)
        self.bb_spinner = gtk.SpinButton(adjustment=bb_adjust, climb_rate=1, digits=0)
        self.bb_spinner.show()
        table.attach(self.bb_spinner, 2, 4, 8, 9)

        label = gtk.Label("PARALLEL_MAKE:")
        label.show()
        table.attach(label, 1, 2, 9, 10)

        pmake_adjust = gtk.Adjustment(value=self.pmake, lower=1, upper=16, step_incr=1)
        self.pmake_spinner = gtk.SpinButton(adjustment=pmake_adjust, climb_rate=1, digits=0)
        self.pmake_spinner.show()
        table.attach(self.pmake_spinner, 2, 4, 9, 10)

        bbox = gtk.HButtonBox()
        bbox.set_spacing(12)
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.show()
        vbox.pack_start(bbox, expand=False, fill=False)
        bake = gtk.Button("Next")
        bake.connect("clicked", self.config_next_clicked_cb)
        bake.show()
        bbox.add(bake)

        return vbox

    def create_recipe_gui(self):
        vbox = gtk.VBox(False, 12)
        vbox.set_border_width(6)
        vbox.show()

        hbox = gtk.HBox(False, 12)
        hbox.show()
        vbox.pack_start(hbox, expand=False, fill=False)

        label = gtk.Label("Base image:")
        label.show()
        hbox.pack_start(label, expand=False, fill=False, padding=6)
        self.image_combo = gtk.ComboBox()
        self.image_combo.show()
        self.image_combo.set_tooltip_text("Selects the image on which to base the created image")
        image_combo_cell = gtk.CellRendererText()
        self.image_combo.pack_start(image_combo_cell, True)
        self.image_combo.add_attribute(image_combo_cell, 'text', self.recipe_model.COL_NAME)
        hbox.pack_start(self.image_combo, expand=False, fill=False, padding=6)
        self.progress = gtk.ProgressBar()
        self.progress.set_size_request(250, -1)
        hbox.pack_end(self.progress, expand=False, fill=False, padding=6)

        ins = gtk.Notebook()
        vbox.pack_start(ins, expand=True, fill=True)
        ins.set_show_tabs(True)
        label = gtk.Label("Recipes")
        label.show()
        ins.append_page(self.recipesaz(), tab_label=label)
        label = gtk.Label("Recipe Collections")
        label.show()
        ins.append_page(self.tasks(), tab_label=label)
        ins.set_current_page(0)
        ins.show_all()

        hbox = gtk.HBox(False, 1)
        hbox.show()
        vbox.pack_start(hbox, expand=False, fill=False, padding=6)
        con = self.contents()
        con.show()
        vbox.pack_start(con, expand=True, fill=True)

        bbox = gtk.HButtonBox()
        bbox.set_spacing(12)
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.show()
        vbox.pack_start(bbox, expand=False, fill=False)
        reset = gtk.Button("Previous")
        reset.connect("clicked", self.recipe_previous_clicked_cb)
        reset.show()
        bbox.add(reset)
        bake = gtk.Button("Build Recipes")
        bake.connect("clicked", self.recipe_next_clicked_cb)
        bake.show()
        bbox.add(bake)

        return vbox

def main (server, eventHandler):
    gobject.threads_init()

    recipemodel = RecipeListModel()
    handler = HobHandler(recipemodel, server)

    layers = server.runCommand(["getVariable", "BBLAYERS"])
    dldir = server.runCommand(["getVariable", "DL_DIR"])
    mach = server.runCommand(["getVariable", "MACHINE"])
    distro = server.runCommand(["getVariable", "DISTRO"]) or "defaultsetup"
    sstatedir = server.runCommand(["getVariable", "SSTATE_DIR"])
    sstatemirror = server.runCommand(["getVariable", "SSTATE_MIRROR"])

    pclasses = server.runCommand(["getVariable", "PACKAGE_CLASSES"]).split(" ")
    pkg, sep, pclass = pclasses[0].rpartition("_")

    bbthread = server.runCommand(["getVariable", "BB_NUMBER_THREADS"])
    if not bbthread:
        bbthread = 1
    else:
        bbthread = int(bbthread)

    pmake = server.runCommand(["getVariable", "PARALLEL_MAKE"])
    if not pmake:
        pmake = 1
    else:
        pmake = int(pmake.lstrip("-j "))

    try:
        # kick the while thing off
        handler.next_command = handler.CFG_PATH_LAYERS
        handler.run_next_command()
    except xmlrpclib.Fault:
        print("XMLRPC Fault getting commandline:\n %s" % x)
        return 1

    window = MainWindow(recipemodel, handler, layers, mach, pclass, distro, bbthread, pmake, dldir, sstatedir, sstatemirror)
    window.show_all ()
    handler.connect("machines-updated", window.update_machines)
    handler.connect("distros-updated", window.update_distros)
    handler.connect("package-formats-found", window.update_package_formats)
    handler.connect("layers-found", window.load_current_layers)
    handler.connect("generating-data", window.busy)
    handler.connect("data-generated", window.data_generated)
    

    # This timeout function regularly probes the event queue to find out if we
    # have any messages waiting for us.
    gobject.timeout_add (100,
                         handler.event_handle_idle_func,
                         eventHandler)

    try:
        gtk.main()
    except EnvironmentError as ioerror:
        # ignore interrupted io
        if ioerror.args[0] == 4:
            pass
    finally:
        server.runCommand(["stateStop"])
