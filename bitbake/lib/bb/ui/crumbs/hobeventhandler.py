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

import gobject
import logging
import tempfile
import datetime

progress_total = 0

class HobHandler(gobject.GObject):

    """
    This object does BitBake event handling for the hob gui.
    """
    __gsignals__ = {
         "layers-avail"       : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE,
                                 (gobject.TYPE_PYOBJECT,)),
         "package-formats-found" : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_PYOBJECT,)),
         "machines-updated"    : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_PYOBJECT,)),
         "distros-updated"     : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_PYOBJECT,)),
         "sdk-machines-updated": (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_PYOBJECT,)),
         "command-succeeded"   : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_INT,)),
         "command-failed"      : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_STRING,)),
         "generating-data"     : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  ()),
         "data-generated"      : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  ()),
    }

    (CFG_AVAIL_LAYERS, CFG_PATH_LAYERS, CFG_FILES_DISTRO, CFG_FILES_MACH, CFG_FILES_SDKMACH, FILES_MATCH_CLASS, PARSE_CONFIG, PARSE_BBFILES, GENERATE_TGTS, BUILD_TARGET_RECIPES, BUILD_TARGET_IMAGE, CMD_END) = range(12)
    (LAYERS_REFRESH, GENERATE_RECIPES, GENERATE_PACKAGES, GENERATE_IMAGE) = range(4)

    def __init__(self, recipemodel, packagemodel, server):
        gobject.GObject.__init__(self)

        self.commands_async = []
        self.generating = False
        self.current_phase = None
        self.building = False
        self.build_queue = []
        self.build_queue_len = 0
        self.package_queue = []

        self.recipe_model = recipemodel
        self.package_model = packagemodel
        self.server = server
        self.error_msg = ""
        self.initcmd = None

    def set_busy(self):
        if not self.generating:
            self.emit("generating-data")
            self.generating = True

    def clear_busy(self):
        if self.generating:
            self.emit("data-generated")
            self.generating = False

    def run_next_command(self, initcmd=None):
        if initcmd != None:
            self.initcmd = initcmd

        if self.commands_async:
            self.set_busy()
            next_command = self.commands_async.pop(0)
        else:
            self.clear_busy()
            if self.initcmd != None:
                self.emit("command-succeeded", self.initcmd)
            return

        if next_command == self.CFG_AVAIL_LAYERS:
            self.server.runCommand(["findCoreBaseFiles", "layers", "conf/layer.conf"])
        elif next_command == self.CFG_PATH_LAYERS:
            self.server.runCommand(["findConfigFilePath", "bblayers.conf"])
        elif next_command == self.CFG_FILES_DISTRO:
            self.server.runCommand(["findConfigFiles", "DISTRO"])
        elif next_command == self.CFG_FILES_MACH:
            self.server.runCommand(["findConfigFiles", "MACHINE"])
        elif next_command == self.CFG_FILES_SDKMACH:
            self.server.runCommand(["findConfigFiles", "MACHINE-SDK"])
        elif next_command == self.FILES_MATCH_CLASS:
            self.server.runCommand(["findFilesMatchingInDir", "rootfs_", "classes"])
        elif next_command == self.PARSE_CONFIG:
            self.server.runCommand(["parseConfigurationFiles", "", ""])
        elif next_command == self.PARSE_BBFILES:
            self.server.runCommand(["parseFiles"])
        elif next_command == self.GENERATE_TGTS:
            self.server.runCommand(["generateTargetsTree", "classes/image.bbclass", [], True])
        elif next_command == self.BUILD_TARGET_RECIPES:
            self.building = True
            self.build_queue_len = len(self.build_queue)
            self.server.runCommand(["buildTargets", self.build_queue, "package_info"])
            self.build_queue = []
        elif next_command == self.BUILD_TARGET_IMAGE:
            self.building = True
            targets = ["hob"]
            self.server.runCommand(["setVariable", "LINGUAS_INSTALL", ""])
            self.server.runCommand(["setVariable", "PACKAGE_INSTALL", " ".join(self.package_queue)])
            if self.toolchain_build:
                pkgs = self.package_queue + [i+'-dev' for i in self.package_queue] + [i+'-dbg' for i in self.package_queue]
                self.server.runCommand(["setVariable", "TOOLCHAIN_TARGET_TASK", " ".join(pkgs)])
                targets.append("hob-toolchain")
            self.server.runCommand(["buildTargets", targets, "build"])

    def handle_event(self, event, window):
        if not event:
            return

        if isinstance(event, bb.event.PackageInfo):
            self.build_queue_len -= 1
            if event._pkginfolist:
                pniter = self.package_model.populate_recipe(event._recipe)
                for pkginfo in event._pkginfolist:
                    self.package_model.populate(pniter, pkginfo)
            if self.build_queue_len == 0:
                self.package_model.map_pn_path()
                self.package_model.emit("packagelist-populated")

        if self.building:
            self.current_phase = "building"
            window.build.handle_event(event, window.view_build_progress)

        elif(isinstance(event, logging.LogRecord)):
            if event.levelno >= logging.ERROR:
                self.error_msg += event.msg + '\n'

        elif isinstance(event, bb.event.TargetsTreeGenerated):
            self.current_phase = "data generation"
            if event._model:
                self.recipe_model.populate(event._model)
        elif isinstance(event, bb.event.CoreBaseFilesFound):
            self.current_phase = "configuration lookup"
            paths = event._paths
            self.emit('layers-avail', paths)
        elif isinstance(event, bb.event.ConfigFilesFound):
            self.current_phase = "configuration lookup"
            var = event._variable
            if var == "distro":
            	distros = event._values
            	distros.sort()
            	self.emit("distros-updated", distros)
            elif var == "machine":
                machines = event._values
            	machines.sort()
            	self.emit("machines-updated", machines)
            elif var == "machine-sdk":
                sdk_machines = event._values
                sdk_machines.sort()
                self.emit("sdk-machines-updated", sdk_machines)
        elif isinstance(event, bb.event.ConfigFilePathFound):
            self.current_phase = "configuration lookup"
        elif isinstance(event, bb.event.FilesMatchingFound):
            self.current_phase = "configuration lookup"
            # FIXME: hard coding, should at least be a variable shared between
            # here and the caller
            if event._pattern == "rootfs_":
                formats = []
                for match in event._matches:
                    classname, sep, cls = match.rpartition(".")
                    fs, sep, format = classname.rpartition("_")
                    formats.append(format)
                formats.sort()
                self.emit("package-formats-found", formats)
        elif isinstance(event, bb.command.CommandCompleted):
            self.current_phase = None
            self.run_next_command()
        elif isinstance(event, bb.command.CommandFailed):
            self.commands_async = []
            if self.error_msg:
                self.emit("command-failed", self.error_msg)
                self.error_msg = ""
        elif isinstance(event, (bb.event.ParseStarted, bb.event.CacheLoadStarted, bb.event.TreeDataPreparationStarted)) \
            and window and window.create_recipe_progress:
            if isinstance(event, bb.event.ParseStarted):
                window.create_recipe_progress.set_case_by_num(0)
            elif isinstance(event, bb.event.CacheLoadStarted):
                window.create_recipe_progress.set_case_by_num(1)
            window.create_recipe_progress.update(0, None, bb.event.getName(event))
            window.create_recipe_progress.set_title("Parsing recipes: ")
        elif isinstance(event, (bb.event.ParseProgress, bb.event.CacheLoadProgress, bb.event.TreeDataPreparationProgress)) \
            and window and window.create_recipe_progress:
            window.create_recipe_progress.update(event.current, event.total, bb.event.getName(event))
            window.create_recipe_progress.set_title("Parsing recipes: ")
        elif isinstance(event, (bb.event.ParseCompleted, bb.event.CacheLoadCompleted, bb.event.TreeDataPreparationCompleted)) \
            and window and window.create_recipe_progress:
            window.create_recipe_progress.update(event.total, event.total, bb.event.getName(event))
            window.create_recipe_progress.set_title("Parsing recipes: ")
        return

    def event_handle_idle_func (self, eventHandler, window):
        # Consume as many messages as we can in the time available to us
        event = eventHandler.getEvent()
        while event:
            self.handle_event(event, window)
            event = eventHandler.getEvent()
        return True

    def init_cooker(self):
        self.server.runCommand(["initCooker"])

    def layer_refresh(self, bblayers):
        self.server.runCommand(["initCooker"])
        self.server.runCommand(["setVariable", "BBLAYERS", " ".join(bblayers)])
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.CFG_FILES_DISTRO)
        self.commands_async.append(self.CFG_FILES_MACH)
        self.commands_async.append(self.CFG_FILES_SDKMACH)
        self.commands_async.append(self.FILES_MATCH_CLASS)
        self.run_next_command(self.LAYERS_REFRESH)

    def set_extra_inherit(self, bbclass):
        inherits = self.server.runCommand(["getVariable", "INHERIT"]) or ""
        inherits = inherits + " " + bbclass
        self.server.runCommand(["setVariable", "INHERIT", inherits])

    def set_bblayers(self, bblayers):
        self.server.runCommand(["setVariable", "BBLAYERS", " ".join(bblayers)])

    def set_machine(self, machine):
        self.server.runCommand(["setVariable", "MACHINE", machine])

    def set_sdk_machine(self, sdk_machine):
        self.server.runCommand(["setVariable", "SDKMACHINE", sdk_machine])

    def set_distro(self, distro):
        self.server.runCommand(["setVariable", "DISTRO", distro])

    def set_package_format(self, format):
        package_classes = ""
        for pkgfmt in format.split():
            package_classes += ("package_%s" % pkgfmt + " ")
        self.server.runCommand(["setVariable", "PACKAGE_CLASSES", package_classes])

    def set_bbthreads(self, threads):
        self.server.runCommand(["setVariable", "BB_NUMBER_THREADS", threads])

    def set_pmake(self, threads):
        pmake = "-j %s" % threads
        self.server.runCommand(["setVariable", "PARALLEL_MAKE", pmake])

    def set_dl_dir(self, directory):
        self.server.runCommand(["setVariable", "DL_DIR", directory])

    def set_sstate_dir(self, directory):
        self.server.runCommand(["setVariable", "SSTATE_DIR", directory])

    def set_sstate_mirror(self, url):
        self.server.runCommand(["setVariable", "SSTATE_MIRROR", url])

    def set_extra_size(self, image_extra_size):
        self.server.runCommand(["setVariable", "IMAGE_ROOTFS_EXTRA_SPACE", str(image_extra_size)])

    def set_incompatible_license(self, incompat_license):
        self.server.runCommand(["setVariable", "INCOMPATIBLE_LICENSE", incompat_license])

    def set_extra_config(self, extra_setting):
        for key in extra_setting.keys():
            value = extra_setting[key]
            self.server.runCommand(["setVariable", key, value])

    def generate_recipes(self):
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.GENERATE_TGTS)
        self.run_next_command(self.GENERATE_RECIPES)
                 
    def generate_packages(self, tgts):
        targets = []
        targets.extend(tgts)
        self.build_queue = targets
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.PARSE_BBFILES)
        self.commands_async.append(self.BUILD_TARGET_RECIPES)
        self.run_next_command(self.GENERATE_PACKAGES)

    def generate_image(self, recipes, packages, fast_mode=False, toolchain_build=False):
        self.build_queue = recipes
        self.package_queue = packages
        self.toolchain_build = toolchain_build
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.PARSE_BBFILES)
        if fast_mode:
            self.commands_async.append(self.BUILD_TARGET_RECIPES)
        self.commands_async.append(self.BUILD_TARGET_IMAGE)
        self.run_next_command(self.GENERATE_IMAGE)

    def build_failed_async(self):
        self.initcmd = None
        self.commands_async = []

    def cancel_build(self, force=False):
        if force:
            # Force the cooker to stop as quickly as possible
            self.server.runCommand(["stateStop"])
        else:
            # Wait for tasks to complete before shutting down, this helps
            # leave the workdir in a usable state
            self.server.runCommand(["stateShutdown"])


