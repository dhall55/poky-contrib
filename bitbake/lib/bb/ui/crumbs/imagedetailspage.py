#!/usr/bin/env python
#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2012        Intel Corporation
#
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

import gobject
import gtk
from bb.ui.crumbs.hobcolor import HobColors
from bb.ui.crumbs.hobwidget import hic, HobViewTable, HobAltButton, HobButton
from bb.ui.crumbs.hobpages import HobPage
import subprocess

#
# ImageDetailsPage
#
class ImageDetailsPage (HobPage):

    __columns__ = [{
            'col_name' : 'Image name',
            'col_id'   : 0,
            'col_style': 'text',
            'col_min'  : 500,
            'col_max'  : 500
        },{
            'col_name' : 'Image size',
            'col_id'   : 1,
            'col_style': 'text',
            'col_min'  : 100,
            'col_max'  : 100
        },{
            'col_name' : 'Select',
            'col_id'   : 2,
            'col_style': 'radio toggle',
            'col_min'  : 100,
            'col_max'  : 100
        }]

    class DetailBox (gtk.EventBox):
        def __init__(self, widget = None, varlist = None, vallist = None, icon = None, button = None, color = HobColors.LIGHT_GRAY):
            gtk.EventBox.__init__(self)

            # set color
            style = self.get_style().copy()
            style.bg[gtk.STATE_NORMAL] = self.get_colormap().alloc_color(color, False, False)
            self.set_style(style)

            self.hbox = gtk.HBox()
            self.hbox.set_border_width(15)
            self.add(self.hbox)

            total_rows = 0
            if widget:
                total_rows = 10
            if varlist and vallist:
                # pack the icon and the text on the left
                total_rows += len(varlist)
            self.table = gtk.Table(total_rows, 20, True)
            self.table.set_row_spacings(6)
            self.table.set_size_request(100, -1)
            self.hbox.pack_start(self.table, expand=True, fill=True, padding=15)

            colid = 0
            rowid = 0
            self.line_widgets = {}
            if icon:
                self.table.attach(icon, colid, colid + 2, 0, 1)
                colid = colid + 2
            if widget:
                self.table.attach(widget, colid, 20, 0, 10)
                rowid = 10
            if varlist and vallist:
                for row in range(rowid, total_rows):
                    index = row - rowid
                    self.line_widgets[varlist[index]] = self.text2label(varlist[index], vallist[index])
                    self.table.attach(self.line_widgets[varlist[index]], colid, 20, row, row + 1)
            # pack the button on the right
            if button:
                self.hbox.pack_end(button, expand=False, fill=False)

        def update_line_widgets(self, variable, value):
            if len(self.line_widgets) == 0:
                return
            if not isinstance(self.line_widgets[variable], gtk.Label):
                return
            self.line_widgets[variable].set_markup(self.format_line(variable, value))

        def format_line(self, variable, value):
            markup = "<span weight=\'bold\'>%s</span>" % variable
            markup += "<span weight=\'normal\' foreground=\'#1c1c1c\' font_desc=\'14px\'>%s</span>" % value
            return markup

        def text2label(self, variable, value):
            # append the name:value to the left box
            # such as "Name: hob-core-minimal-variant-2011-12-15-beagleboard"
            label = gtk.Label()
            label.set_alignment(0.0, 0.5)
            label.set_markup(self.format_line(variable, value))
            return label

    def __init__(self, builder):
        super(ImageDetailsPage, self).__init__(builder, "Image details")

        self.image_store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
        self.button_ids = {}
        self.details_bottom_buttons = gtk.HBox(False, 6)
        self.create_visual_elements()

    def create_visual_elements(self):
        # create visual elements
        # create the toolbar
        self.toolbar = gtk.Toolbar()
        self.toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.toolbar.set_style(gtk.TOOLBAR_BOTH)

        template_button = self.append_toolbar_button(self.toolbar,
            "Templates",
            hic.ICON_TEMPLATES_DISPLAY_FILE,
            hic.ICON_TEMPLATES_HOVER_FILE,
            "Load a previously saved template",
            self.template_button_clicked_cb)
        my_images_button = self.append_toolbar_button(self.toolbar,
            "Images",
            hic.ICON_IMAGES_DISPLAY_FILE,
            hic.ICON_IMAGES_HOVER_FILE,
            "Open previously built images",
            self.my_images_button_clicked_cb)
        settings_button = self.append_toolbar_button(self.toolbar,
            "Settings",
            hic.ICON_SETTINGS_DISPLAY_FILE,
            hic.ICON_SETTINGS_HOVER_FILE,
            "View additional build settings",
            self.settings_button_clicked_cb)

        self.details_top_buttons = self.add_onto_top_bar(self.toolbar)

    def _remove_all_widget(self):
        children = self.get_children() or []
        for child in children:
            self.remove(child)
        children = self.box_group_area.get_children() or []
        for child in children:
            self.box_group_area.remove(child)
        children = self.details_bottom_buttons.get_children() or []
        for child in children:
            self.details_bottom_buttons.remove(child)

    def show_page(self, step):
        build_succeeded = (step == self.builder.IMAGE_GENERATED)
        image_addr = self.builder.parameters.image_addr
        image_names = self.builder.parameters.image_names
        if build_succeeded:
            machine = self.builder.configuration.curr_mach
            base_image = self.builder.recipe_model.get_selected_image()
            layers = self.builder.configuration.layers
            pkg_num = "%s" % len(self.builder.package_model.get_selected_packages())
        else:
            pkg_num = "N/A"

        # remove
        for button_id, button in self.button_ids.items():
            button.disconnect(button_id)
        self._remove_all_widget()

        # repack
        self.pack_start(self.details_top_buttons, expand=False, fill=False)
        self.pack_start(self.group_align, expand=True, fill=True)

        self.build_result = None
        if build_succeeded:
            # building is the previous step
            icon = gtk.Image()
            pixmap_path = hic.ICON_INDI_CONFIRM_FILE
            color = HobColors.RUNNING
            pix_buffer = gtk.gdk.pixbuf_new_from_file(pixmap_path)
            icon.set_from_pixbuf(pix_buffer)
            varlist = [""]
            vallist = ["Your image is ready"]
            self.build_result = self.DetailBox(varlist=varlist, vallist=vallist, icon=icon, color=color)
            self.box_group_area.pack_start(self.build_result, expand=False, fill=False)

        # create the buttons at the bottom first because the buttons are used in apply_button_per_image()
        if build_succeeded:
            self.buttonlist = ["Build new image", "Save as template", "Run image", "Deploy image"]
        else: # get to this page from "My images"
            self.buttonlist = ["Build new image", "Run image", "Deploy image"]

        # Name
        self.image_store.clear()
        default_toggled = ""
        default_image_size = 0
        num_toggled = 0
        i = 0
        for image_name in image_names:
            image_size = HobPage._size_to_string(os.stat(os.path.join(image_addr, image_name)).st_size)
            is_toggled = (self.test_type_runnable(image_name) and self.test_mach_runnable(image_name)) \
                or self.test_deployable(image_name)

            if not default_toggled:
                if i == (len(image_names) - 1):
                    is_toggled = True
                self.image_store.set(self.image_store.append(), 0, image_name, 1, image_size, 2, is_toggled)
                if is_toggled:
                    default_image_size = image_size
                    default_toggled = image_name

            else:
                self.image_store.set(self.image_store.append(), 0, image_name, 1, image_size, 2, False)
            i = i + 1
            num_toggled += is_toggled

        self.create_bottom_buttons(self.buttonlist, default_toggled)

        if build_succeeded and (num_toggled < 2):
            varlist = ["Name: ", "Directory: "]
            vallist = []
            vallist.append(image_name.split('.')[0])
            vallist.append(image_addr)
            image_table = None
        else:
            varlist = None
            vallist = None
            image_table = HobViewTable(self.__columns__)
            image_table.set_model(self.image_store)
            image_table.connect("row-activated", self.row_activated_cb)
            image_table.connect_group_selection(self.table_selected_cb)

        view_files_button = HobAltButton("View files")
        view_files_button.connect("clicked", self.view_files_clicked_cb, image_addr)
        view_files_button.set_tooltip_text("Open the directory containing the image files")
        self.image_detail = self.DetailBox(widget=image_table, varlist=varlist, vallist=vallist, button=view_files_button)
        self.box_group_area.pack_start(self.image_detail, expand=True, fill=True)

        # Machine, Base image and Layers
        layer_num_limit = 15
        varlist = ["Machine: ", "Base image: ", "Layers: "]
        vallist = []
        self.setting_detail = None
        if build_succeeded:
            vallist.append(machine)
            vallist.append(base_image)
            i = 0
            for layer in layers:
                varlist.append(" - ")
                if i > layer_num_limit:
                    break
                i += 1
            vallist.append("")
            i = 0
            for layer in layers:
                if i > layer_num_limit:
                    break
                elif i == layer_num_limit:
                    vallist.append("and more...")
                else:
                    vallist.append(layer)
                i += 1

            edit_config_button = HobAltButton("Edit configuration")
            edit_config_button.set_tooltip_text("Edit machine, base image and recipes")
            edit_config_button.connect("clicked", self.edit_config_button_clicked_cb)
            self.setting_detail = self.DetailBox(varlist=varlist, vallist=vallist, button=edit_config_button)
            self.box_group_area.pack_start(self.setting_detail, expand=True, fill=True)

        # Packages included, and Total image size
        varlist = ["Packages included: ", "Total image size: "]
        vallist = []
        vallist.append(pkg_num)
        vallist.append(default_image_size)
        if build_succeeded:
            edit_packages_button = HobAltButton("Edit packages")
            edit_packages_button.set_tooltip_text("Edit the packages included in your image")
            edit_packages_button.connect("clicked", self.edit_packages_button_clicked_cb)
        else: # get to this page from "My images"
            edit_packages_button = None
        self.package_detail = self.DetailBox(varlist=varlist, vallist=vallist, button=edit_packages_button)
        self.box_group_area.pack_start(self.package_detail, expand=False, fill=False)

        # pack the buttons at the bottom, at this time they are already created.
        self.box_group_area.pack_end(self.details_bottom_buttons, expand=False, fill=False)

        self.show_all()

    def view_files_clicked_cb(self, button, image_addr):
        subprocess.call("xdg-open /%s" % image_addr, shell=True)

    def refresh_package_detail_box(self, image_size):
        self.package_detail.update_line_widgets("Total image size: ", image_size)

    def test_type_runnable(self, image_name):
        type_runnable = False
        for t in self.builder.parameters.runnable_image_types:
            if image_name.endswith(t):
                type_runnable = True
                break
        return type_runnable

    def test_mach_runnable(self, image_name):
        mach_runnable = False
        for t in self.builder.parameters.runnable_machine_patterns:
            if t in image_name:
                mach_runnable = True
                break
        return mach_runnable

    def test_deployable(self, image_name):
        deployable = False
        for t in self.builder.parameters.deployable_image_types:
            if image_name.endswith(t):
                deployable = True
                break
        return deployable

    def table_selected_cb(self, selection):
        model, paths = selection.get_selected_rows()
        if (not model) or (not paths):
            return

        path = paths[0]
        columnid = 2
        iter = model.get_iter_first()
        while iter:
            rowpath = model.get_path(iter)
            model[rowpath][columnid] = False
            iter = model.iter_next(iter)

        model[path][columnid] = True
        self.refresh_package_detail_box(model[path][1])

        image_name = model[path][0]

        # remove
        for button_id, button in self.button_ids.items():
            button.disconnect(button_id)
        self._remove_all_widget()
        # repack
        self.pack_start(self.details_top_buttons, expand=False, fill=False)
        self.pack_start(self.group_align, expand=True, fill=True)
        if self.build_result:
            self.box_group_area.pack_start(self.build_result, expand=False, fill=False)
        self.box_group_area.pack_start(self.image_detail, expand=True, fill=True)
        if self.setting_detail:
            self.box_group_area.pack_start(self.setting_detail, expand=False, fill=False)
        self.box_group_area.pack_start(self.package_detail, expand=False, fill=False)
        self.create_bottom_buttons(self.buttonlist, image_name)
        self.box_group_area.pack_end(self.details_bottom_buttons, expand=False, fill=False)
        self.show_all()

    def row_activated_cb(self, table, model, path):
        if not model:
            return
        iter = model.get_iter(path)
        image_name = model[path][0]
        if iter and model[path][2] == 'runnable':
            kernel_name, kernel_number = self.get_kernel_file_name(image_name)
            self.builder.runqemu_image(image_name, kernel_name, kernel_number)

    def create_bottom_buttons(self, buttonlist, image_name):
        # Create the buttons at the bottom
        created = False
        packed = False
        self.button_ids = {}

        # create button "Deploy image"
        name = "Deploy image"
        if name in buttonlist and self.test_deployable(image_name):
            deploy_button = HobButton('Deploy image')
            deploy_button.set_size_request(205, 49)
            deploy_button.set_tooltip_text("Burn a live image to a USB drive or flash memory")
            deploy_button.set_flags(gtk.CAN_DEFAULT)
            button_id = deploy_button.connect("clicked", self.deploy_button_clicked_cb, image_name)
            self.button_ids[button_id] = deploy_button
            self.details_bottom_buttons.pack_end(deploy_button, expand=False, fill=False)
            created = True
            packed = True

        name = "Run image"
        if name in buttonlist and self.test_type_runnable(image_name) and self.test_mach_runnable(image_name):
            if created == True:
                # separator
                label = gtk.Label(" or ")
                self.details_bottom_buttons.pack_end(label, expand=False, fill=False)

                # create button "Run image"
                run_button = HobAltButton("Run image")
            else:
                # create button "Run image" as the primary button
                run_button = HobButton("Run image")
                run_button.set_size_request(205, 49)
                run_button.set_flags(gtk.CAN_DEFAULT)
                packed = True
            run_button.set_tooltip_text("Start up an image with qemu emulator")
            button_id = run_button.connect("clicked", self.run_button_clicked_cb, image_name)
            self.button_ids[button_id] = run_button
            self.details_bottom_buttons.pack_end(run_button, expand=False, fill=False)
            created = True

        name = "Save as template"
        if name in buttonlist:
            if created == True:
                # separator
                label = gtk.Label(" or ")
                self.details_bottom_buttons.pack_end(label, expand=False, fill=False)

                # create button "Save as template"
                save_button = HobAltButton("Save as template")
            else:
                save_button = HobButton("Save as template")
                save_button.set_size_request(205, 49)
                save_button.set_flags(gtk.CAN_DEFAULT)
                packed = True
            save_button.set_tooltip_text("Save the image configuration for reuse")
            button_id = save_button.connect("clicked", self.save_button_clicked_cb)
            self.button_ids[button_id] = save_button
            self.details_bottom_buttons.pack_end(save_button, expand=False, fill=False)
            create = True

        name = "Build new image"
        if name in buttonlist:
            # create button "Build new image"
            if packed:
                build_new_button = HobAltButton("Build new image")
                self.details_bottom_buttons.pack_start(build_new_button, expand=False, fill=False)
            else:
                build_new_button = HobButton("Build new image")
                build_new_button.set_size_request(205, 49)
                build_new_button.set_flags(gtk.CAN_DEFAULT)
                self.details_bottom_buttons.pack_end(build_new_button, expand=False, fill=False)
            build_new_button.set_tooltip_text("Create a new image from scratch")
            button_id = build_new_button.connect("clicked", self.build_new_button_clicked_cb)
            self.button_ids[button_id] = build_new_button

    def get_kernel_file_name(self, image_name):
        name_list = []
        kernel_name = ""
        if image_name:
            image_path = os.path.join(self.builder.parameters.image_addr)
            files = [f for f in os.listdir(image_path) if f[0] <> '.']
            for check_file in files:
                if check_file.endswith(".bin"):
                    if  self.test_mach_runnable(check_file):
                        selected_machine = self.builder.configuration.curr_mach
                        if selected_machine in check_file:
                            kernel_name = check_file
                    if not os.path.islink(os.path.join(image_path, check_file)):
                        name_list.append(check_file)

        return kernel_name, len(name_list)

    def save_button_clicked_cb(self, button):
        self.builder.show_save_template_dialog()

    def deploy_button_clicked_cb(self, button, image_name):
        self.builder.deploy_image(image_name)

    def run_button_clicked_cb(self, button, image_name):
        self.builder.runqemu_image(image_name)

    def build_new_button_clicked_cb(self, button):
        self.builder.initiate_new_build_async()

    def edit_config_button_clicked_cb(self, button):
        self.builder.show_configuration()

    def edit_packages_button_clicked_cb(self, button):
        self.builder.show_packages(ask=False)

    def template_button_clicked_cb(self, button):
        response, path = self.builder.show_load_template_dialog()
        if not response:
            return
        if path:
            self.builder.load_template(path)

    def my_images_button_clicked_cb(self, button):
        self.builder.show_load_my_images_dialog()

    def settings_button_clicked_cb(self, button):
        # Create an advanced settings dialog
        response, settings_changed = self.builder.show_adv_settings_dialog()
        if not response:
            return
        if settings_changed:
            self.builder.reparse_post_adv_settings()
