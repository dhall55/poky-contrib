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
import copy
from bb.ui.crumbs.hobwidget import HobWidget

class LayerSelection (gtk.Window):
    def __init__(self, split_model, handler, params):
        self.split_model = split_model
        self.handler = handler
        self.layers = params["layer"].split()
        self.layers_default = copy.copy(self.layers)
        self.layers_avail = None
        self.layer_store = None
                
    def load_avail_layers(self, handler, layers):
        self.layers_avail = layers

    def layer_selection_ok_cb(self, button, window):
        model = self.layer_store

        it = model.get_iter_first()
        layers = []
        while it:
            if self.split_model:
                inc = model.get_value(it, 1)
                if inc:
                    layers.append(model.get_value(it, 0))
            else:
                layers.append(model.get_value(it, 0))
            it = model.iter_next(it)

        if self.layers != layers:
            self.layers = layers
            self.handler.layer_refresh(self.layers)

        window.destroy()

    def main(self, button):
        window = gtk.Dialog("Layer Selection", None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT  | gtk.DIALOG_NO_SEPARATOR)

        window.set_border_width(20)
        window.set_default_size(400, 250)

        hbox_top = gtk.HBox()
        window.set_border_width(12)
        window.vbox.pack_start(hbox_top, expand=False, fill=False)

        label = HobWidget.gen_label_widget("<span weight=\"bold\" font_desc='12'>Select Layers:</span>")
        hbox_top.pack_start(label, expand=False, fill=False)

        tooltip = "Layer is a collection of bb files and conf files"
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        image.set_tooltip_text(tooltip)
        hbox_top.pack_end(image, expand=False, fill=False)

        layer_widget, self.layer_store = HobWidget.gen_layer_widget(self.split_model, self.layers, self.layers_avail, window, None)

        window.vbox.pack_start(layer_widget, expand=True, fill=True)

        separator = gtk.HSeparator()
        window.vbox.pack_start(separator, False, True, 5)
        separator.show()

        hbox_button = gtk.HBox()
        window.vbox.pack_end(hbox_button, expand=False, fill=False)
        hbox_button.show()

        label = HobWidget.gen_label_widget("<i>'meta' is Core layer for Yocto images</i>\n"
        "<span weight=\"bold\">Please do not remove it</span>")
        hbox_button.pack_start(label, expand=False, fill=False)

        bbox = gtk.HButtonBox()
        bbox.set_spacing(20)
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.show()
        hbox_button.pack_end(bbox, expand=True, fill=True)
        button = gtk.Button(stock=gtk.STOCK_OK)
        button.connect("clicked", self.layer_selection_ok_cb, window)
        button.show()
        bbox.pack_end(button, expand=True, fill=True)

        window.show_all()

        response = window.run()
        window.destroy()


