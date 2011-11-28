# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Dongxiao xu <dongxiao.xu@intel.com>
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
import glib
import gobject
from bb.ui.crumbs.hig import CrumbsDialog

class HobWidget():
    @classmethod
    def _toggle_cb(cls, cell, path, model, column):
        it = model.get_iter(path)
        val = model.get_value(it, column)
        val = not val
        model.set(it, column, val)

    @classmethod
    def _pkgfmt_up_clicked_cb(cls, button, tree_selection):
        (model, it) = tree_selection.get_selected()
        if not it:
            return
        path = model.get_path(it)
        if path[0] <= 0:
            return

        pre_it = model.get_iter_first()
        if not pre_it:
            return
        else:
            while model.iter_next(pre_it) :
                if model.get_value(model.iter_next(pre_it), 1) != model.get_value(it, 1):
                    pre_it = model.iter_next(pre_it)
                else:
                    break

            cur_index = model.get_value(it, 0)
            pre_index = cur_index
            if pre_it:
                model.set(pre_it, 0, pre_index)
            cur_index = cur_index - 1
            model.set(it, 0, cur_index)

    @classmethod
    def _pkgfmt_down_clicked_cb(cls, button, tree_selection):
        (model, it) = tree_selection.get_selected()
        if not it:
            return
        next_it = model.iter_next(it)
        if not next_it:
            return
        cur_index = model.get_value(it, 0)
        next_index = cur_index
        model.set(next_it, 0, next_index)
        cur_index = cur_index + 1
        model.set(it, 0, cur_index)

    @classmethod
    def _tree_selection_changed_cb(cls, tree_selection, button1, button2):
        (model, it) = tree_selection.get_selected()        
        inc = model.get_value(it, 2)
        if inc:
            button1.set_sensitive(True)
            button2.set_sensitive(True)
        else:
            button1.set_sensitive(False)
            button2.set_sensitive(False)

    @classmethod
    def _sort_func(cls, model, iter1, iter2, data):
        val1 = model.get_value(iter1, 0)
        val2 = model.get_value(iter2, 0)
        inc1 = model.get_value(iter1, 2)
        inc2 = model.get_value(iter2, 2)
        if inc1 != inc2:
            return inc2 - inc1
        else:
            return val1 - val2

    @classmethod
    def gen_pkgfmt_widget(cls, curr_package_format, all_package_format, tooltip=""):
        pkgfmt_hbox = gtk.HBox(False, 15)

        pkgfmt_store = gtk.ListStore(int, str, gobject.TYPE_BOOLEAN)
        for format in curr_package_format.split():
            pkgfmt_store.set(pkgfmt_store.append(), 1, format, 2, True)
        for format in all_package_format:
            if format not in curr_package_format:
                pkgfmt_store.set(pkgfmt_store.append(), 1, format, 2, False)
        pkgfmt_tree = gtk.TreeView(pkgfmt_store)
        pkgfmt_tree.set_headers_clickable(True)
        pkgfmt_tree.set_headers_visible(False)
        tree_selection = pkgfmt_tree.get_selection()
        tree_selection.set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('NO')
        col.set_sort_column_id(0)
        col.set_sort_order(gtk.SORT_ASCENDING)
        col.set_clickable(False)
        col1 = gtk.TreeViewColumn('TYPE')
        col1.set_min_width(130)
        col1.set_max_width(140)
        col2 = gtk.TreeViewColumn('INCLUDED')
        col2.set_min_width(60)
        col2.set_max_width(70)
        pkgfmt_tree.append_column(col1)
        pkgfmt_tree.append_column(col2)
        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell1.set_property('width-chars', 10)
        cell2 = gtk.CellRendererToggle()
        cell2.set_property('activatable', True)
        cell2.connect("toggled", cls._toggle_cb, pkgfmt_store, 2)
        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_end(cell2, True)
        col.set_attributes(cell, text=0)
        col1.set_attributes(cell1, text=1)
        col2.set_attributes(cell2, active=2)

        pkgfmt_store.set_sort_func(0, cls._sort_func, None)
        pkgfmt_store.set_sort_column_id(0, gtk.SORT_ASCENDING)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(pkgfmt_tree)
        scroll.set_size_request(200,60)
        pkgfmt_hbox.pack_start(scroll, False, False, 0)

        vbox = gtk.VBox(False, 5)
        pkgfmt_hbox.pack_start(vbox, False, False, 15)

        up = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_MENU)
        up.set_image(image)
        up.set_size_request(50,30)
        up.connect("clicked", cls._pkgfmt_up_clicked_cb, tree_selection)
        vbox.pack_start(up, False, False, 5)

        down = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_MENU)
        down.set_image(image)
        down.set_size_request(50,30)
        down.connect("clicked", cls._pkgfmt_down_clicked_cb, tree_selection)
        vbox.pack_start(down, False, False, 5)
        tree_selection.connect("changed", cls._tree_selection_changed_cb, up, down)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        image.set_tooltip_text(tooltip)
        pkgfmt_hbox.pack_start(image, expand=False, fill=False)

        pkgfmt_hbox.show_all()

        return pkgfmt_hbox, pkgfmt_store

    @classmethod
    def gen_combo_widget(cls, curr_item, all_item, tooltip=""):
        hbox = gtk.HBox(False, 10)
        combo = gtk.combo_box_new_text()
        hbox.pack_start(combo, expand=False, fill=False)

        index = 0
        for item in all_item or []:
            combo.append_text(item)
            if item == curr_item:
                combo.set_active(index)
            index += 1

        image = gtk.Image()
        image.show()
        image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        image.set_tooltip_text(tooltip)

        hbox.pack_start(image, expand=False, fill=False)

        hbox.show_all()

        return hbox, combo

    @classmethod
    def gen_label_widget(cls, content):
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup(content)
        label.show()
        return label

    @classmethod
    def _select_path_cb(cls, action, parent, entry):
        dialog = gtk.FileChooserDialog("", parent,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            path = dialog.get_filename()
            entry.set_text(path)

        dialog.destroy()

    @classmethod
    def gen_entry_widget(cls, split_model, content, parent, tooltip=""):
        hbox = gtk.HBox(False, 10)
        entry = gtk.Entry()
        entry.set_text(content)

        if split_model:
            hbox.pack_start(entry, expand=False, fill=False)
        else:
            table = gtk.Table(1, 10, True)
            hbox.pack_start(table, expand=False, fill=False)
            table.attach(entry, 0, 9, 0, 1)
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_BUTTON)
            open_button = gtk.Button()
            open_button.set_image(image)
            open_button.connect("clicked", cls._select_path_cb, parent, entry)
            table.attach(open_button, 9, 10, 0, 1)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        image.set_tooltip_text(tooltip)
        hbox.pack_start(image, expand=False, fill=False)

        hbox.show_all()

        return hbox, entry

    @classmethod
    def gen_spinner_widget(cls, content, lower, upper, tooltip=""):
        hbox = gtk.HBox(False, 10)
        adjust = gtk.Adjustment(value=content, lower=lower, upper=upper, step_incr=1)
        spinner = gtk.SpinButton(adjustment=adjust, climb_rate=1, digits=0)
                        
        spinner.set_value(content)
        hbox.pack_start(spinner, expand=False, fill=False)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        image.set_tooltip_text(tooltip)
        hbox.pack_start(image, expand=False, fill=False)

        hbox.show_all()

        return hbox, spinner

    @classmethod
    def conf_error(cls, parent, lbl):
        dialog = CrumbsDialog(parent, lbl)
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        response = dialog.run()
        dialog.destroy()

    @classmethod
    def _add_layer_cb(cls, action, layer_store, parent):
        dialog = gtk.FileChooserDialog("Add new layer", parent,
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
            import os
            import os.path
            layers = []
            it = layer_store.get_iter_first()
            while it:
                layers.append(layer_store.get_value(it, 0))
                it = layer_store.iter_next(it)

            if not path:
                lbl += "it is an invalid path."
            elif not os.path.exists(path+"/conf/layer.conf"):
                lbl += "there is no layer.conf inside the directory."
            elif path in layers:
                lbl += "it is already in loaded layers."
            else:
                layer_store.append([path])
                return
            cls.conf_error(parent, lbl)

    @classmethod
    def _del_layer_cb(cls, action, tree_selection, layer_store):
        model, iter = tree_selection.get_selected()
        if iter:
            layer_store.remove(iter)

    @classmethod
    def _toggle_layer_cb(cls, cell, path, layer_store):
        name = layer_store[path][0]
        toggle = not layer_store[path][1]
        layer_store[path][1] = toggle

    @classmethod
    def gen_layer_widget(cls, split_model, layers, layers_avail, window, tooltip=""):
        hbox = gtk.HBox(False, 10)

        layer_tv = gtk.TreeView()
        layer_tv.set_rules_hint(True)
        layer_tv.set_headers_visible(False)
        tree_selection = layer_tv.get_selection()
        tree_selection.set_mode(gtk.SELECTION_SINGLE)

        col0= gtk.TreeViewColumn('Path')
        cell0 = gtk.CellRendererText()
        cell0.set_padding(5,2)
        col0.pack_start(cell0, True)
        col0.set_attributes(cell0, text=0)
        layer_tv.append_column(col0)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(layer_tv)

        table_layer = gtk.Table(2, 10, False)
        hbox.pack_start(table_layer, expand=True, fill=True)

        if split_model:
            table_layer.attach(scroll, 0, 10, 0, 2)

            layer_store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
            for layer in layers:
                layer_store.set(layer_store.append(), 0, layer, 1, True)
            for layer in layers_avail:
                if layer not in layers:
                    layer_store.set(layer_store.append(), 0, layer, 1, False)

            col1 = gtk.TreeViewColumn('Included')
            layer_tv.append_column(col1)

            cell1 = gtk.CellRendererToggle()
            cell1.connect("toggled", cls._toggle_layer_cb, layer_store)
            col1.pack_start(cell1, True)
            col1.set_attributes(cell1, active=1)

        else:
            table_layer.attach(scroll, 0, 10, 0, 1)

            layer_store = gtk.ListStore(gobject.TYPE_STRING)
            for layer in layers:
                layer_store.set(layer_store.append(), 0, layer)

            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_MENU)
            add_button = gtk.Button()
            add_button.set_image(image)
            add_button.connect("clicked", cls._add_layer_cb, layer_store, window)
            table_layer.attach(add_button, 0, 5, 1, 2, gtk.EXPAND | gtk.FILL, 0, 0, 0)
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_REMOVE,gtk.ICON_SIZE_MENU)
            del_button = gtk.Button()
            del_button.set_image(image)
            del_button.connect("clicked", cls._del_layer_cb, tree_selection, layer_store)
            table_layer.attach(del_button, 5, 10, 1, 2, gtk.EXPAND | gtk.FILL, 0, 0, 0)
        layer_tv.set_model(layer_store)

        hbox.show_all()

        return hbox, layer_store

    @classmethod
    def toggle_item_idle_cb(cls, window, listmodel, path, image):
        """
        As the operations which we're calling on the model can take
        a significant amount of time (in the order of seconds) during which
        the GUI is unresponsive as the main loop is blocked perform them in
        an idle function which at least enables us to set the busy cursor
        before the UI is blocked giving the appearance of being responsive.
        """
        # Whether the item is currently included
        inc = listmodel[path][listmodel.COL_INC]
        if not inc:
            listmodel.include_item(item_path=path,
                                   binb="User Selected",
                                   image_contents=image)
        else:
            listmodel.exclude_item(item_path=path)

        window.set_sensitive(True)
        window.get_root_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        return False

    @classmethod
    def toggle_item(cls, window, path, model, listmodel, image=False):
        window.set_sensitive(False)
        window.get_root_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        # Convert path to path in original model
        opath = model.convert_path_to_child_path(path)
        # This is a potentially length call which can block the
        # main loop, therefore do the work in an idle func to keep
        # the UI responsive
        glib.idle_add(cls.toggle_item_idle_cb, window, listmodel, opath, image)

    @classmethod
    def toggle_include_cb(cls, cell, path, window, tv, listmodel):
        model = tv.get_model()
        cls.toggle_item(window, path, model, listmodel)

    @classmethod
    def toggle_selection_include_cb(cls, cell, path, window, tv, listmodel):
        # there's an extra layer of models in the recipes case.
        sort_model = tv.get_model()
        cpath = sort_model.convert_path_to_child_path(path)
        cls.toggle_item(window, cpath, sort_model.get_model(), listmodel)

    @classmethod
    def _on_add_item_clicked(cls, button, model):
        new_item = ["##KEY##", "##VALUE##"]

        iter = model.append()
        model.set (iter,
            0, new_item[0],
            1, new_item[1],
       )


    @classmethod
    def _on_remove_item_clicked(cls, button, treeview):

        selection = treeview.get_selection()
        model, iter = selection.get_selected()

        if iter:
            path = model.get_path(iter)[0]
            model.remove(iter)

    @classmethod
    def _on_cell_edited(cls, cell, path_string, new_text, model):
        it = model.get_iter_from_string(path_string)
        column = cell.get_data("column")
        model.set(it, column, new_text)


    @classmethod
    def gen_editable_settings(cls, setting, tooltip=""):
        setting_hbox = gtk.HBox(False, 10)

        vbox = gtk.VBox(False, 10)
        setting_hbox.pack_start(vbox, expand=False, fill=False)

        setting_store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        for key in setting.keys():
            setting_store.set(setting_store.append(), 0, key, 1, setting[key])

        setting_tree = gtk.TreeView(setting_store)
        setting_tree.set_headers_visible(True)
        setting_tree.set_size_request(300, 100)

        col = gtk.TreeViewColumn('Key')
        col.set_min_width(100)
        col.set_max_width(150)
        col.set_resizable(True)
        col1 = gtk.TreeViewColumn('Value')
        col1.set_min_width(100)
        col1.set_max_width(150)
        col1.set_resizable(True)
        setting_tree.append_column(col)
        setting_tree.append_column(col1)
        cell = gtk.CellRendererText()
        cell.set_property('width-chars', 10)
        cell.set_property('editable', True)
        cell.set_data("column", 0)
        cell.connect("edited", cls._on_cell_edited, setting_store)
        cell1 = gtk.CellRendererText()
        cell1.set_property('width-chars', 10)
        cell1.set_property('editable', True)
        cell1.set_data("column", 1)
        cell1.connect("edited", cls._on_cell_edited, setting_store)
        col.pack_start(cell, True)
        col1.pack_end(cell1, True)
        col.set_attributes(cell, text=0)
        col1.set_attributes(cell1, text=1)

        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(setting_tree)
        vbox.pack_start(scroll, expand=False, fill=False)

        # some buttons
        hbox = gtk.HBox(True, 4)
        vbox.pack_start(hbox, False, False)

        button = gtk.Button(stock=gtk.STOCK_ADD)
        button.connect("clicked", cls._on_add_item_clicked, setting_store)
        hbox.pack_start(button)

        button = gtk.Button(stock=gtk.STOCK_REMOVE)
        button.connect("clicked", cls._on_remove_item_clicked, setting_tree)
        hbox.pack_start(button)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        image.set_tooltip_text(tooltip)
        setting_hbox.pack_start(image, expand=False, fill=False)

        return setting_hbox, setting_store

