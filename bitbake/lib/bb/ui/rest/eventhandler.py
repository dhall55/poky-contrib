#
# Copyright (C) 2011        Intel Corporation
#
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

import logging
import runningbuild

class Eventhandler:

    """
    This object does BitBake event handling for the web hob.
    """

    (CFG_AVAIL_LAYERS, CFG_PATH_LAYERS, CFG_FILES_DISTRO, CFG_FILES_MACH, CFG_FILES_SDKMACH, FILES_MATCH_CLASS, PARSE_CONFIG, PARSE_BBFILES, GENERATE_TGTS, BUILD_TARGET_RECIPES, BUILD_TARGET_IMAGE, CMD_END) = range(12)
    (GENERATE_ASYNC_CONFIGS,LAYERS_REFRESH, GENERATE_RECIPES, GENERATE_PACKAGES, GENERATE_IMAGE) = range(1,6)

    def __init__(self, server):

        self.commands_async = []
        self.building = False
        self.build_queue = []
        self.build_queue_len = 0
        self.package_queue = []

        self.server = server
        self.error_msg = ""
        self.initcmd = None

        self.package_model_List = []
        self.event_result = None
        self.current_completed_action = ''
        self.runningbuild = runningbuild.RunningBuild()

    def run_next_command(self, initcmd=None):
        if initcmd != None:
            self.initcmd = initcmd

        if self.commands_async:
            next_command = self.commands_async.pop(0)
        else:
            if self.initcmd != None:
                if self.initcmd == self.GENERATE_ASYNC_CONFIGS:
                    self.current_completed_action = 'ASYNC_CONFIGS_GENERATED'
                elif self.initcmd == self.LAYERS_REFRESH:
                    self.current_completed_action = 'LAYERS_REFRESH_COMPLETED'
                elif self.initcmd == self.GENERATE_RECIPES:
                    self.current_completed_action = 'PARSE_RECIPES_COMPLETED'
                elif self.initcmd == self.GENERATE_PACKAGES:
                    self.current_completed_action = 'BUILD_PACKAGES_COMPLETED'
                elif self.initcmd == self.GENERATE_IMAGE:
                    self.current_completed_action = 'BUILD_IMAGE_COMPLETED'
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

    def handle_event(self, event):
        if not event:
            return

        if self.event_result:
            self.event_result = None

        if isinstance(event, bb.event.PackageInfo):
            self.build_queue_len -= 1
            if event._pkginfolist and self.build_queue_len >= 0:
                self.package_model_List.append({'package': event._recipe,
                                                'package_value': event._pkginfolist
                                                })

        if self.building:
            if isinstance(event, bb.event.BuildCompleted):
                self.building = False
                failures = int(event._failures)
                if (failures >= 1):
                    self.event_result = {'event': bb.event.getName(event),
                                         'value':'build-failed'
                                        }
                else:
                    self.event_result = {'event': bb.event.getName(event),
                                         'value': self.package_model_List
                                        }

                self.package_model_List = []
            elif isinstance(event, bb.command.CommandFailed):
                self.event_result = {'event': bb.event.getName(event),
                                      'value':''
                                    }
            else:
                self.event_result = self.runningbuild.handle_event(event)

            return self.event_result

        elif(isinstance(event, logging.LogRecord)):
            if event.levelno >= logging.ERROR:
                self.error_msg += event.msg + '\n'

        elif isinstance(event, bb.event.TargetsTreeGenerated):

            if event._model:
                eventResult = {'model': event._model}
            else:
                eventResult = {}

            self.event_result = {'event': bb.event.getName(event),
                             'value': eventResult
                            }
        elif isinstance(event, bb.event.CoreBaseFilesFound):
            paths = event._paths

            self.event_result = {'event': bb.event.getName(event),
                                 'value': {'paths': _paths}
                                }
        elif isinstance(event, bb.event.ConfigFilesFound):
            var = event._variable

            if var == "distro":
                distros = event._values
                distros.sort()
                eventResult = {'distros': distros}
            elif var == "machine":
                machines = event._values
                machines.sort()
                eventResult = {'machines': machines}
            elif var == "machine-sdk":
                sdk_machines = event._values
                sdk_machines.sort()
                eventResult = {'machines-sdk': sdk_machines}

            self.event_result = {'event': bb.event.getName(event),
                                 'value': eventResult
                                }
        elif isinstance(event, bb.event.ConfigFilePathFound):
            pass
        elif isinstance(event, bb.event.FilesMatchingFound):
            if event._pattern == "rootfs_":
                formats = []
                for match in event._matches:
                    classname, sep, cls = match.rpartition(".")
                    fs, sep, format = classname.rpartition("_")
                    formats.append(format)
                formats.sort()

                self.event_result = {'event': bb.event.getName(event),
                                     'value': {'formats': formats}
                                    }
        elif isinstance(event, bb.command.CommandCompleted):
            self.run_next_command()
            if self.current_completed_action:
                self.event_result = {'event': bb.event.getName(event),
                                     'value': self.current_completed_action
                                    }
                self.current_completed_action = ''
        elif isinstance(event, bb.command.CommandFailed):
            self.commands_async = []
            if self.error_msg:
                self.event_result = {'event': bb.event.getName(event),
                                     'value': {'error_msg': self.error_msg}
                                    }
                self.error_msg = ""
        elif isinstance(event, (bb.event.ParseStarted,
                                bb.event.CacheLoadStarted,
                                bb.event.TreeDataPreparationStarted)):
            if isinstance(event, bb.event.ParseStarted):
                self.event_result = {'event': bb.event.getName(event),
                                     'value': {}
                                    }
            elif isinstance(event, bb.event.CacheLoadStarted):
                self.event_result = {'event': bb.event.getName(event),
                                     'value': {}
                                    }
        elif isinstance(event, (bb.event.ParseProgress,
                                bb.event.CacheLoadProgress,
                                bb.event.TreeDataPreparationProgress)):
            self.event_result = {'event': bb.event.getName(event),
                                 'value': {'current': event.current,
                                           'total': event.total
                                          }
                                }
        elif isinstance(event, (bb.event.ParseCompleted,
                                bb.event.CacheLoadCompleted,
                                bb.event.TreeDataPreparationCompleted)):
           self.event_result = {'event': bb.event.getName(event),
                                'value': {'total': event.total}
                               }

        return self.event_result

    def get_config_item(self, param):
        return self.server.runCommand(["getVariable", param]) or ""

    def get_cpu_count(self):
        return self.server.runCommand(["getCpuCount"])

    def set_user_config(self, vars):
        self.init_cooker()
        self.set_bblayers(vars['layers'])
        self.set_machine(vars['curr_mach'])
        self.set_package_format(vars['curr_package_format'])
        self.set_distro(vars['curr_distro'])
        self.set_dl_dir(vars['dldir'])
        self.set_sstate_dir(vars['sstatedir'])
        self.set_sstate_mirror(vars['sstatemirror'])
        self.set_pmake(vars['pmake'])
        self.set_bbthreads(vars['bbthread'])
        self.set_extra_size(vars['image_extra_size'])
        self.set_incompatible_license(vars['incompat_license'])
        self.set_sdk_machine(vars['curr_sdk_machine'])
        self.set_extra_config(vars['extra_setting'])
        self.set_extra_inherit("packageinfo")

    def init_cooker(self):
        self.server.runCommand(["initCooker"])

    def reset_cooker(self):
        self.server.runCommand(["resetCooker"])

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

    def generate_async_configs(self):
        self.commands_async.append(self.CFG_PATH_LAYERS)
        self.commands_async.append(self.CFG_FILES_DISTRO)
        self.commands_async.append(self.CFG_FILES_MACH)
        self.commands_async.append(self.CFG_FILES_SDKMACH)
        self.commands_async.append(self.FILES_MATCH_CLASS)
        self.run_next_command(self.GENERATE_ASYNC_CONFIGS)

    def layer_refresh(self, bblayers):
        self.server.runCommand(["initCooker"])
        self.server.runCommand(["setVariable", "BBLAYERS", " ".join(bblayers)])
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.CFG_FILES_DISTRO)
        self.commands_async.append(self.CFG_FILES_MACH)
        self.commands_async.append(self.CFG_FILES_SDKMACH)
        self.commands_async.append(self.FILES_MATCH_CLASS)
        self.run_next_command(self.LAYERS_REFRESH)

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