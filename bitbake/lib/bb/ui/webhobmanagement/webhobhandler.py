class WebhobHandler:
    (INITIALIZE_CONFIGURATION, GENERATE_CONFIGURATION, GENERATE_RECIPES, GENERATE_PACKAGES, GENERATE_IMAGE, POPULATE_PACKAGEINFO, SANITY_CHECK) = range(7)
    (PATH_LAYERS, FILES_DISTRO, FILES_MACH, FILES_SDKMACH, MATCH_CLASS, PARSE_CONFIG, SANITY_CHECK, GNERATE_TGTS, GENERATE_PKGINFO, BUILD_RECIPES, BUILD_IMAGE) = range(11)

    def __init__(self, server, recipe_model=None, package_model=None):
        self.recipe_model = recipe_model
        self.package_model = package_model

        self.commands_async = []
        self.recipe_queue = []
        self.package_queue = []

        self.server = server
        self.error_msg = ""
        self.completed = False
 
        self.action = None

    def runCommand(self, commandline):
#        print '--runCommand--::',commandline
        try:
            return self.server.runCommand(commandline)
        except Exception as e:
            self.commands_async = []
            return None

    def run_next_command(self):
        if self.commands_async:
            next_command = self.commands_async.pop(0)
        else:
            return True

        if next_command == self.PATH_LAYERS:
            self.runCommand(["findConfigFilePath", "bblayers.conf"])
        elif next_command == self.FILES_DISTRO:
            self.runCommand(["findConfigFiles", "DISTRO"])
        elif next_command == self.FILES_MACH:
            self.runCommand(["findConfigFiles", "MACHINE"])
        elif next_command == self.FILES_SDKMACH:
            self.runCommand(["findConfigFiles", "MACHINE-SDK"])
        elif next_command == self.MATCH_CLASS:
            self.runCommand(["findFilesMatchingInDir", "rootfs_", "classes"])
        elif next_command == self.PARSE_CONFIG:
            self.runCommand(["parseConfigurationFiles", "", ""])
        elif next_command == self.GNERATE_TGTS:
            self.runCommand(["generateTargetsTree", "classes/image.bbclass", []])
        elif next_command == self.GENERATE_PKGINFO:
            self.runCommand(["triggerEvent", "bb.event.RequestPackageInfo()"])
        elif next_command == self.SANITY_CHECK:
            self.runCommand(["triggerEvent", "bb.event.SanityCheck()"])
        elif next_command == self.BUILD_RECIPES:
            self.runCommand(["buildTargets", self.recipe_queue, self.default_task])
            self.recipe_queue = []
        elif next_command == self.BUILD_IMAGE:
            targets = [self.image]
            if self.package_queue:
                self.runCommand(["setVariable", "LINGUAS_INSTALL", ""])
                self.runCommand(["setVariable", "PACKAGE_INSTALL", " ".join(self.package_queue)])
            if self.toolchain_packages:
                self.runCommand(["setVariable", "TOOLCHAIN_TARGET_TASK", " ".join(self.toolchain_packages)])
                targets.append(self.toolchain)
            self.runCommand(["buildTargets", targets, self.default_task])

    def getEvents(self):
        events = self.server.getEvent()
        if events:
            last_event = events[-1].get('event')
            if last_event == 'CommandCompleted':
                self.completed = self.run_next_command()
                if self.completed:
                    msg = {'event':'Done',
                           'result':'successed'}
                    events.append(msg)
            elif last_event == 'SanityCheckPassed':
                self.run_next_command()
            elif last_event == 'PackageInfo':
                self.run_next_command()
            elif last_event == 'CommandFailed':
                self.commands_async = []
                msg = {'event':'Done',
                       'result':'failed'}
                events.append(msg)
        return events

    def init_cooker(self):
        self.runCommand(["initCooker"])

    def set_extra_inherit(self, bbclass):
        inherits = self.runCommand(["getVariable", "INHERIT"]) or ""
        inherits = inherits + " " + bbclass
        self.runCommand(["setVariable", "INHERIT", inherits])

    def set_bblayers(self, bblayers):
        self.runCommand(["setVariable", "BBLAYERS", " ".join(bblayers)])

    def set_machine(self, machine):
        if machine:
            self.runCommand(["setVariable", "MACHINE", machine])

    def set_sdk_machine(self, sdk_machine):
        self.runCommand(["setVariable", "SDKMACHINE", sdk_machine])

    def set_image_fstypes(self, image_fstypes):
        self.runCommand(["setVariable", "IMAGE_FSTYPES", image_fstypes])

    def set_distro(self, distro):
        self.runCommand(["setVariable", "DISTRO", distro])

    def set_package_format(self, format):
        package_classes = ""
        for pkgfmt in format.split():
            package_classes += ("package_%s" % pkgfmt + " ")
        self.runCommand(["setVariable", "PACKAGE_CLASSES", package_classes])

    def set_bbthreads(self, threads):
        self.runCommand(["setVariable", "BB_NUMBER_THREADS", threads])

    def set_pmake(self, threads):
        pmake = "-j %s" % threads
        self.runCommand(["setVariable", "PARALLEL_MAKE", pmake])

    def set_dl_dir(self, directory):
        self.runCommand(["setVariable", "DL_DIR", directory])

    def set_sstate_dir(self, directory):
        self.runCommand(["setVariable", "SSTATE_DIR", directory])

    def set_sstate_mirror(self, url):
        self.runCommand(["setVariable", "SSTATE_MIRROR", url])

    def set_extra_size(self, image_extra_size):
        self.runCommand(["setVariable", "IMAGE_ROOTFS_EXTRA_SPACE", str(image_extra_size)])

    def set_rootfs_size(self, image_rootfs_size):
        self.runCommand(["setVariable", "IMAGE_ROOTFS_SIZE", str(image_rootfs_size)])

    def set_incompatible_license(self, incompat_license):
        self.runCommand(["setVariable", "INCOMPATIBLE_LICENSE", incompat_license])

    def set_extra_config(self, extra_setting):
        for key in extra_setting.keys():
            value = extra_setting[key]
            self.runCommand(["setVariable", key, value])

    def set_config_filter(self, config_filter):
        self.runCommand(["setConfFilter", config_filter])

    def set_http_proxy(self, http_proxy):
        self.runCommand(["setVariable", "http_proxy", http_proxy])

    def set_https_proxy(self, https_proxy):
        self.runCommand(["setVariable", "https_proxy", https_proxy])

    def set_ftp_proxy(self, ftp_proxy):
        self.runCommand(["setVariable", "ftp_proxy", ftp_proxy])

    def set_git_proxy(self, host, port):
        self.runCommand(["setVariable", "GIT_PROXY_HOST", host])
        self.runCommand(["setVariable", "GIT_PROXY_PORT", port])

    def set_cvs_proxy(self, host, port):
        self.runCommand(["setVariable", "CVS_PROXY_HOST", host])
        self.runCommand(["setVariable", "CVS_PROXY_PORT", port])

    def request_package_info(self):
        self.action = self.POPULATE_PACKAGEINFO
        self.commands_async.append(self.GENERATE_PKGINFO)
        self.run_next_command()

    def trigger_sanity_check(self):
        self.action = self.SANITY_CHECK
        self.commands_async.append(self.SANITY_CHECK)
        self.run_next_command()

    def initialize_configuration(self):
        self.action = self.INITIALIZE_CONFIGURATION
        self.init_cooker()
        self.set_extra_inherit("image_types")
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.PATH_LAYERS)
        self.commands_async.append(self.FILES_DISTRO)
        self.commands_async.append(self.FILES_MACH)
        self.commands_async.append(self.FILES_SDKMACH)
        self.commands_async.append(self.MATCH_CLASS)
        self.run_next_command()

    def generate_configuration(self):
        self.action = self.GENERATE_CONFIGURATION
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.PATH_LAYERS)
        self.commands_async.append(self.FILES_DISTRO)
        self.commands_async.append(self.FILES_MACH)
        self.commands_async.append(self.FILES_SDKMACH)
        self.commands_async.append(self.MATCH_CLASS)
        self.run_next_command()


    def generate_recipes(self):
        self.action = self.GENERATE_RECIPES
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.GNERATE_TGTS)
        self.run_next_command()

    def generate_packages(self, tgts, default_task="build"):
        self.action = self.GENERATE_PACKAGES
        targets = []
        targets.extend(tgts)
        self.recipe_queue = targets
        self.default_task = default_task
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.BUILD_RECIPES)
        self.run_next_command()

    def generate_image(self, image, toolchain, image_packages=[], toolchain_packages=[], default_task="build"):
        self.action = self.GENERATE_IMAGE
        self.image = image
        self.toolchain = toolchain
        self.package_queue = image_packages
        self.toolchain_packages = toolchain_packages
        self.default_task = default_task
        self.commands_async.append(self.PARSE_CONFIG)
        self.commands_async.append(self.BUILD_IMAGE)
        self.run_next_command()

    def cancel_parse(self):
        self.runCommand(["stateStop"])

    def cancel_build(self, force=False):
        if force:
            # Force the cooker to stop as quickly as possible
            self.runCommand(["stateStop"])
        else:
            # Wait for tasks to complete before shutting down, this helps
            # leave the workdir in a usable state
            self.runCommand(["stateShutdown"])

    def _remove_redundant(self, string):
        ret = []
        for i in string.split():
            if i not in ret:
                ret.append(i)
        return " ".join(ret)

    def get_parameters(self):
        # retrieve the parameters from bitbake
        params = {}
        params["core_base"] = self.runCommand(["getVariable", "COREBASE"]) or ""
        hob_layer = params["core_base"] + "/meta-hob"
        params["layer"] = self.runCommand(["getVariable", "BBLAYERS"]) or ""
        if hob_layer not in params["layer"].split():
            params["layer"] += (" " + hob_layer)
        params["dldir"] = self.runCommand(["getVariable", "DL_DIR"]) or ""
        params["machine"] = self.runCommand(["getVariable", "MACHINE"]) or ""
        params["distro"] = self.runCommand(["getVariable", "DISTRO"]) or "defaultsetup"
        params["pclass"] = self.runCommand(["getVariable", "PACKAGE_CLASSES"]) or ""
        params["sstatedir"] = self.runCommand(["getVariable", "SSTATE_DIR"]) or ""
        params["sstatemirror"] = self.runCommand(["getVariable", "SSTATE_MIRROR"]) or ""

        num_threads = self.runCommand(["getCpuCount"])
        if not num_threads:
            num_threads = 1
            max_threads = 65536
        else:
            try:
                num_threads = int(num_threads)
                max_threads = 16 * num_threads
            except:
                num_threads = 1
                max_threads = 65536
        params["max_threads"] = max_threads

        bbthread = self.runCommand(["getVariable", "BB_NUMBER_THREADS"])
        if not bbthread:
            bbthread = num_threads
        else:
            try:
                bbthread = int(bbthread)
            except:
                bbthread = num_threads
        params["bbthread"] = bbthread

        pmake = self.runCommand(["getVariable", "PARALLEL_MAKE"])
        if not pmake:
            pmake = num_threads
        elif isinstance(pmake, int):
            pass
        else:
            try:
                pmake = int(pmake.lstrip("-j "))
            except:
                pmake = num_threads
        params["pmake"] = "-j %s" % pmake

        params["image_addr"] = self.runCommand(["getVariable", "DEPLOY_DIR_IMAGE"]) or ""

        image_extra_size = self.runCommand(["getVariable", "IMAGE_ROOTFS_EXTRA_SPACE"])
        if not image_extra_size:
            image_extra_size = 0
        else:
            try:
                image_extra_size = int(image_extra_size)
            except:
                image_extra_size = 0
        params["image_extra_size"] = image_extra_size

        image_rootfs_size = self.runCommand(["getVariable", "IMAGE_ROOTFS_SIZE"])
        if not image_rootfs_size:
            image_rootfs_size = 0
        else:
            try:
                image_rootfs_size = int(image_rootfs_size)
            except:
                image_rootfs_size = 0
        params["image_rootfs_size"] = image_rootfs_size

        image_overhead_factor = self.runCommand(["getVariable", "IMAGE_OVERHEAD_FACTOR"])
        if not image_overhead_factor:
            image_overhead_factor = 1
        else:
            try:
                image_overhead_factor = float(image_overhead_factor)
            except:
                image_overhead_factor = 1
        params['image_overhead_factor'] = image_overhead_factor

        params["incompat_license"] = self._remove_redundant(self.runCommand(["getVariable", "INCOMPATIBLE_LICENSE"]) or "")
        params["sdk_machine"] = self.runCommand(["getVariable", "SDKMACHINE"]) or self.runCommand(["getVariable", "SDK_ARCH"]) or ""

        params["image_fstypes"] = self._remove_redundant(self.runCommand(["getVariable", "IMAGE_FSTYPES"]) or "")

        params["image_types"] = self._remove_redundant(self.runCommand(["getVariable", "IMAGE_TYPES"]) or "")

        params["conf_version"] = self.runCommand(["getVariable", "CONF_VERSION"]) or ""
        params["lconf_version"] = self.runCommand(["getVariable", "LCONF_VERSION"]) or ""

        params["runnable_image_types"] = self._remove_redundant(self.runCommand(["getVariable", "RUNNABLE_IMAGE_TYPES"]) or "")
        params["runnable_machine_patterns"] = self._remove_redundant(self.runCommand(["getVariable", "RUNNABLE_MACHINE_PATTERNS"]) or "")
        params["deployable_image_types"] = self._remove_redundant(self.runCommand(["getVariable", "DEPLOYABLE_IMAGE_TYPES"]) or "")
        params["kernel_image_type"] = self.runCommand(["getVariable", "KERNEL_IMAGETYPE"]) or ""
        params["tmpdir"] = self.runCommand(["getVariable", "TMPDIR"]) or ""
        params["distro_version"] = self.runCommand(["getVariable", "DISTRO_VERSION"]) or ""
        params["target_os"] = self.runCommand(["getVariable", "TARGET_OS"]) or ""
        params["target_arch"] = self.runCommand(["getVariable", "TARGET_ARCH"]) or ""
        params["tune_pkgarch"] = self.runCommand(["getVariable", "TUNE_PKGARCH"])  or ""
        params["bb_version"] = self.runCommand(["getVariable", "BB_MIN_VERSION"]) or ""

        params["default_task"] = self.runCommand(["getVariable", "BB_DEFAULT_TASK"]) or "build"

        params["git_proxy_host"] = self.runCommand(["getVariable", "GIT_PROXY_HOST"]) or ""
        params["git_proxy_port"] = self.runCommand(["getVariable", "GIT_PROXY_PORT"]) or ""

        params["http_proxy"] = self.runCommand(["getVariable", "http_proxy"]) or ""
        params["ftp_proxy"] = self.runCommand(["getVariable", "ftp_proxy"]) or ""
        params["https_proxy"] = self.runCommand(["getVariable", "https_proxy"]) or ""

        params["cvs_proxy_host"] = self.runCommand(["getVariable", "CVS_PROXY_HOST"]) or ""

        params["image_white_pattern"] = self.runCommand(["getVariable", "BBUI_IMAGE_WHITE_PATTERN"]) or ""

        return params

if __name__ == '__main__':
    import sys
    import time
    from wsconnection import Connection
    from pprint import pprint
    server = Connection('http://localhost:8888/?wsdl')
    ret = None

    #    bblayers = ['/home/xiaotong/workspace/python/poky-contrib/meta','/home/xiaotong/workspace/python/poky-contrib/meta-yocto', '/home/xiaotong/workspace/python/poky-contrib/meta-hob']
    bblayers = ['/home/xiaotong/workspace/python/poky-contrib/meta', '/home/xiaotong/workspace/python/poky-contrib/meta-hob']

    handler = WebhobHandler(server)

    handler.init_cooker()

    handler.generate_image('core-image-minimal', 'hob-toolchain', image_packages=[], toolchain_packages=[], default_task="build")
#    handler.set_extra_inherit("image_types")
#    handler.set_bblayers(bblayers)
#    print server.runCommand(["getVariable", "BBLAYERS"])
#    handler.generate_params()

    while True:
        time.sleep(1)
        event=handler.getEvents()
        if isinstance(event, list):
            for i in event:
                if i['event'] == 'LogRecord':
                    if i['levelno'] >= i['logging_ERROR']:
                         pprint('LOG ERROR: '+i['msg'])
                else:
                    pprint(i)

            if event.pop(-1).get('event', None) == 'DONE':
#                pprint(handler.get_parameters())
                break
#
