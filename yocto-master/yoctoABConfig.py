################################################################################
# Yocto Build Server Developer Configuration
################################################################################
# Elizabeth Flanagan <elizabeth.flanagan@intel.com>
################################################################################
# Copyright (C) 2011-2012 Intel Corp.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import copy, random, os, datetime 
from time import strftime
from email.Utils import formatdate
from twisted.python import log
from buildbot.changes.pb import PBChangeSource
from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.process.buildstep import BuildStep, LoggingBuildStep, LoggedRemoteCommand, RemoteShellCommand
from buildbot.scheduler import Triggerable
from buildbot.scheduler import Scheduler
from buildbot.scheduler import Periodic
from buildbot.scheduler import Nightly
from buildbot.schedulers import triggerable
from buildbot.steps.trigger import Trigger
from buildbot.steps import blocker
from buildbot.process import buildstep
from buildbot.status.results import SUCCESS, FAILURE
import buildbot.steps.blocker
from buildbot.steps import shell
from buildbot.steps.shell import ShellCommand
from buildbot.steps.source import Git
from buildbot.process.properties import Property
from buildbot.steps.slave import SetPropertiesFromEnv

yocto_projname = "Yocto"
yocto_projurl = "http://yoctoproject.org/"
yocto_sources = []
yocto_sources.append(PBChangeSource())
yocto_sched = []
yocto_builders = []
defaultenv = {}
layerid = 0

SOURCE_DL_DIR = os.environ.get("SOURCE_DL_DIR")
LSB_SSTATE_DIR = os.environ.get("LSB_SSTATE_DIR")
SOURCE_SSTATE_DIR = os.environ.get("SOURCE_SSTATE_DIR")
CLEAN_SOURCE_DIR = os.environ.get("CLEAN_SOURCE_DIR")
PUBLISH_BUILDS = os.environ.get("PUBLISH_BUILDS")
PUBLISH_SOURCE_MIRROR = os.environ.get("PUBLISH_SOURCE_MIRROR")
PUBLISH_SSTATE = os.environ.get("PUBLISH_SSTATE")
BUILD_PUBLISH_DIR = os.environ.get("BUILD_PUBLISH_DIR")
BUILD_HISTORY_COLLECT = os.environ.get("BUILD_HISTORY_COLLECT")
BUILD_HISTORY_DIR = os.environ.get("BUILD_HISTORY_DIR")
BUILD_HISTORY_REPO = os.environ.get("BUILD_HISTORY_REPO")
SSTATE_PUBLISH_DIR = os.environ.get("SSTATE_PUBLISH_DIR")
SOURCE_PUBLISH_DIR = os.environ.get("SOURCE_PUBLISH_DIR")
EMGD_DRIVER_DIR = os.environ.get("EMGD_DRIVER_DIR")
SLAVEBASEDIR = os.environ.get("SLAVEBASEDIR")
if not BUILD_PUBLISH_DIR:
    BUILD_PUBLISH_DIR = "/tmp"

# Trying to access Properties within a factory can sometimes be problematic.
# This is here for convenience.
defaultenv['ENABLE_SWABBER'] = ""
defaultenv['WORKDIR'] = ""
defaultenv['FuzzArch'] = ""
defaultenv['FuzzImage'] = ""
defaultenv['FuzzSDK'] = ""
defaultenv['machine'] = ""
defaultenv['DEST'] = ""
defaultenv['BRANCH'] = ""
defaultenv['SDKMACHINE'] = "i686"
defaultenv['DL_DIR'] = SOURCE_DL_DIR
defaultenv['LSB_SSTATE_DIR'] = LSB_SSTATE_DIR
defaultenv['SSTATE_DIR'] = SOURCE_SSTATE_DIR
defaultenv['BUILD_HISTORY_COLLECT'] = BUILD_HISTORY_COLLECT
defaultenv['BUILD_HISTORY_DIR'] = BUILD_HISTORY_DIR
defaultenv['BUILD_HISTORY_REPO'] = BUILD_HISTORY_REPO
defaultenv['EMGD_DRIVER_DIR'] = EMGD_DRIVER_DIR
defaultenv['SLAVEBASEDIR'] = SLAVEBASEDIR

class NoOp(buildstep.BuildStep):
    """
    A build step that does nothing except finish with a caller-
    supplied status (default SUCCESS).
    """
    parms = buildstep.BuildStep.parms + ['result']

    result = SUCCESS
    flunkOnFailure = True

    def start(self):
        self.step_status.setText([self.name])
        self.finished(self.result)

class setDest(LoggingBuildStep):
    renderables = [ 'workdir', 'btarget' ]
    
    def __init__(self, workdir=None, btarget=None, **kwargs):
        LoggingBuildStep.__init__(self, **kwargs)
        self.workdir = workdir
        self.btarget = btarget
        self.description = ["Setting", "Destination"]
        self.addFactoryArguments(workdir=workdir, btarget=btarget)

    def describe(self, done=False):
        return self.description

    def setStepStatus(self, step_status):
        LoggingBuildStep.setStepStatus(self, step_status)

    def setDefaultWorkdir(self, workdir):
        self.workdir = self.workdir or workdir

    def start(self):
        try:
	        self.getProperty('DEST')
        except:
            DEST = os.path.join(BUILD_PUBLISH_DIR.strip('"').strip("'"), self.btarget)
            REV = 1
            DEST_DATE=datetime.datetime.now().strftime("%Y%m%d")
            while os.path.exists(os.path.join(DEST, DEST_DATE + "-" + str(REV))):
                REV = REV + 1
                print os.path.join(DEST, DEST_DATE + "-" + str(REV)) 
            DEST=os.path.join(os.path.join(DEST, DEST_DATE + "-" + str(REV)))
            self.setProperty('DEST', DEST)
	return self.finished(SUCCESS)

class YoctoBlocker(buildbot.steps.blocker.Blocker):

    VALID_IDLE_POLICIES = buildbot.steps.blocker.Blocker.VALID_IDLE_POLICIES + ("run",)

    def _getBuildStatus(self, botmaster, builderName):
        try:
            builder = botmaster.builders[builderName]
        except KeyError:
            raise BadStepError(
                "no builder named %r" % builderName)
        
        myBuildStatus = self.build.getStatus()
        builderStatus = builder.builder_status
        matchingBuild = None

        all_builds = (builderStatus.buildCache.values() +
                      builderStatus.getCurrentBuilds())

        for buildStatus in all_builds:
            if self.buildsMatch(myBuildStatus, buildStatus):
                matchingBuild = buildStatus
                break

        if matchingBuild is None:
            msg = "no matching builds found in builder %r" % builderName
            if self.idlePolicy == "error":
                raise BadStepError(msg + " (is it idle?)")
            elif self.idlePolicy == "ignore":
                self._log(msg + ": skipping it")
                return None
            elif self.idlePolicy == "block":
                self._log(msg + ": will block until it starts a build")
                self._blocking_builders.add(builderStatus)
                return None
            elif self.idlePolicy == "run":
                self._log(msg + ": start build for break the block")
                from buildbot.process.builder import BuilderControl
                from buildbot.sourcestamp import SourceStamp
                bc = BuilderControl(builder, botmaster)
                bc.submitBuildRequest(
                    SourceStamp(),
                    "start for break the block",
                    props = {
                        'uniquebuildnumber': (myBuildStatus.getProperties()['uniquebuildnumber'], 'Build'),
                        }
                    )
                all_builds = (builderStatus.buildCache.values() +
                              builderStatus.getCurrentBuilds())

                for buildStatus in all_builds:
                    if self.buildsMatch(myBuildStatus, buildStatus):
                        matchingBuild = buildStatus
                        break
                self._blocking_builders.add(builderStatus)

        self._log("found builder %r: %r", builderName, builder)
        return matchingBuild

    def buildsMatch(self, buildStatus1, buildStatus2):
        return \
        buildStatus1.getProperties().has_key("DEST") and \
        buildStatus2.getProperties().has_key("DEST") and \
        buildStatus1.getProperties()["DEST"] == \
        buildStatus2.getProperties()["DEST"]

def createBBLayersConf(factory, btarget=None, bsplayer=False, provider=None, buildprovider=None):
    factory.addStep(SetPropertiesFromEnv(variables=["SLAVEBASEDIR"]))
    factory.addStep(ShellCommand(doStepIf=getSlaveBaseDir,
                    env=copy.copy(defaultenv),
                    command='echo "Getting the slave basedir"'))
    BBLAYER = defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + "/build/build/conf/bblayers.conf"
    factory.addStep(ShellCommand(doStepIf=getSlaveBaseDir,
                    env=copy.copy(defaultenv),
                    command='echo "Getting the slave basedir"'))
    factory.addStep(ShellCommand(description="Ensuring a bblayers.conf exists",
                    command=["sh", "-c", WithProperties("echo '' > %s/" + defaultenv['ABTARGET'] + "/build/build/conf/bblayers.conf", 'SLAVEBASEDIR')],
                    timeout=60))
    factory.addStep(ShellCommand(warnOnFailure=True, description="Removing old bblayers.conf",
                    command=["sh", "-c", WithProperties("rm %s/" + defaultenv['ABTARGET'] + "/build/build/conf/bblayers.conf", 'SLAVEBASEDIR')],
                    timeout=60))
    fout = 'LCONF_VERSION = "4" \n'
    fout = fout + 'BBFILES ?="" \n'
    fout = fout + 'BBLAYERS = " \ \n'
    if buildprovider=="yocto":
        fout = fout + defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + "/build/meta \ \n"
        fout = fout + defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + "/build/meta-yocto \ \n"
    elif buildprovider=="oe":
        fout = fout + defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + "/build/meta-openembedded \ \n"
        fout = fout + defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + "/build/meta-openembedded/meta-oe \ \n"
    if bsplayer==True and provider=="intel" and defaultenv['ABTARGET'] != "p1022ds":
        fout = fout + defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + '/build/yocto/meta-intel' + ' \ \n'
        fout = fout + defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + '/build/yocto/meta-intel/meta-' + str(btarget).replace("-noemgd", "") + ' \ \n'
        fout = fout + defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] + '/build/yocto/meta-intel/meta-tlk \ \n'
    elif bsplayer==True and provider=="fsl" and defaultenv['ABTARGET'] == "p1022ds":
        fout = fout + defaultenv['SLAVEBASEDIR'] + defaultenv['ABTARGET'] + '/build/yocto/meta-fsl-ppc \ \n'
    fout = fout + defaultenv['SLAVEBASEDIR'] + defaultenv['ABTARGET'] + '/build/meta-qt3 " \n'
    factory.addStep(ShellCommand(description="Creating bblayers.conf",
                    command="echo '" +  fout + "'>>" + BBLAYER,
                    timeout=60))

def createAutoConf(factory, btarget=None, distro=None, buildhistory=False):
    factory.addStep(SetPropertiesFromEnv(variables=["SLAVEBASEDIR"]))
    factory.addStep(ShellCommand(doStepIf=getSlaveBaseDir,
                    env=copy.copy(defaultenv),
                    command='echo "Getting the slave basedir"'))
    factory.addStep(ShellCommand(description="Ensuring a auto.conf exists",
                    command=["sh", "-c", WithProperties("echo '' > %s/" + defaultenv['ABTARGET'] + "/build/build/conf/auto.conf", 'SLAVEBASEDIR')],
                    timeout=60))
    factory.addStep(ShellCommand(warnOnFailure=True, description="Removing old auto.conf",
                    command=["sh", "-c", WithProperties("rm %s/" + defaultenv['ABTARGET'] + "/build/build/conf/auto.conf", 'SLAVEBASEDIR')],
                    timeout=60))
    AUTOCONF = defaultenv['SLAVEBASEDIR'] + "/" + defaultenv['ABTARGET'] +  "/build/build/conf/auto.conf"
    fout = 'PACKAGE_CLASSES = "package_rpm package_deb package_ipk"\n' 
    fout = fout + 'BB_NUMBER_THREADS = "10"\n'
    fout = fout + 'PARALLEL_MAKE = "-j 16"\n'
    fout = fout + 'SDKMACHINE ?= "i586"\n'
    fout = fout + 'DL_DIR = "' + defaultenv['DL_DIR']+'"\n'
    if str(btarget) == "fri2" or str(btarget) == "crownbay":
        fout = fout + 'LICENSE_FLAGS_WHITELIST = "license_emgd-driver-bin_1.10" \n'
    if "lsb" in distro:
        fout = fout + 'SSTATE_DIR ?= "' + defaultenv['LSB_SSTATE_DIR']+'"\n'
    else:
        fout = fout + 'SSTATE_DIR ?= "' + defaultenv['SSTATE_DIR']+'"\n'
    if "gpl3" in defaultenv['ABTARGET']:
        fout = fout + 'INCOMPATIBLE_LICENSE = "GPLv3" \n'
    if "multilib" in defaultenv['ABTARGET']:
        fout = fout + 'require conf/multilib.conf \n'
        fout = fout + 'MULTILIBS = "multilib:lib32" \n'
        fout = fout + 'DEFAULTTUNE_virtclass-multilib-lib32 = "x86" \n'
    fout = fout + 'MACHINE = "' + str(btarget) + '"\n'
    fout = fout + 'PREMIRRORS = ""\n'
    if defaultenv['ENABLE_SWABBER'] == 'true':
        fout = fout + 'USER_CLASSES += "image-prelink image-swab"\n'
    if PUBLISH_BUILDS == "True":
        fout = fout + 'BB_GENERATE_MIRROR_TARBALLS = "1"\n'           
    factory.addStep(ShellCommand(warnOnFailure=True, description="Ensuring auto.conf removal",
                    command="echo '' >> " + AUTOCONF,
                    timeout=60))
    factory.addStep(ShellCommand(warnOnFailure=True, description="Remove old auto.conf",
                    command="rm " +  AUTOCONF,
                    timeout=60))
    factory.addStep(ShellCommand(description="Creating auto.conf",
                    command="echo '" +  fout + "'>>" + AUTOCONF,
                    timeout=60))
    factory.addStep(SetPropertiesFromEnv(variables=["BUILD_HISTORY_DIR"]))
    factory.addStep(SetPropertiesFromEnv(variables=["BUILD_HISTORY_REPO"]))
    factory.addStep(SetPropertiesFromEnv(variables=["BUILD_HISTORY_COLLECT"]))
    if buildhistory is True and defaultenv['BUILD_HISTORY_COLLECT'] is True:
        fout = fout + 'INHERIT += "buildhistory"\n'
        fout = fout + 'BUILDHISTORY_COMMIT = "1"\n'
        fout = fout + 'BUILDHISTORY_DIR = "' + defaultenv['BUILD_HISTORY_DIR'] + '/' + defaultenv['ABTARGET'] + '/poky-buildhistory"\n'
        fout = fout + 'BUILDHISTORY_PUSH_REPO = "' + defaultenv['BUILD_HISTORY_REPO'] + ' ' + defaultenv['ABTARGET'] + ':' + defaultenv['ABTARGET'] + '"\n'
        factory.addStep(ShellCommand(doStepIf=doMasterTest, description="Adding buildhistory to auto.conf",
                        command="echo '" +  fout + "'>>" + AUTOCONF,
                        timeout=60))
        factory.addStep(ShellCommand(doStepIf=doMasterTest,
                        description="Syncing Local Build History Repo",
                        workdir=defaultenv['BUILD_HISTORY_DIR'] + defaultenv['ABTARGET'] + "/poky-buildhistory",
                        command=["git", "pull", "origin", defaultenv['ABTARGET']],
                        timeout=2000))
    if defaultenv['ENABLE_SWABBER'] == 'True':
        fout = fout + 'USER_CLASSES += "image-prelink image-swab"\n'
    if PUBLISH_SOURCE_MIRROR == "True":
        fout = fout + 'BB_GENERATE_MIRROR_TARBALLS = "1"\n'           
    factory.addStep(ShellCommand(description="Creating auto.conf",
                    command="echo '" +  fout + "'>>" + AUTOCONF,
                    timeout=60))

def doMasterTest(step):
    branch = step.getProperty("branch")
    if branch == "master":
        return True
    else:
        return False

def doNightlyArchTest(step):
    buildername = step.getProperty("buildername")
    branch = step.getProperty("branch")
    if "nightly-" in buildername and buildername != "nightly-meta-intel" and branch == "master" and BUILD_HISTORY_COLLECT is True:
        return True
    else:
        return False

def runBSPLayerPreamble(factory, target, provider):
    factory.addStep(shell.SetProperty(workdir="build", 
                    command="git rev-parse HEAD", 
                    property="POKYHASH"))
    if provider=="intel":
        factory.addStep(ShellCommand, 
                        command="echo 'Checking out git://git.yoctoproject.org/meta-intel.git'",
                        timeout=10)
        factory.addStep(ShellCommand(workdir="build/yocto/", command=["git", "clone",  "git://git.yoctoproject.org/meta-intel.git"], timeout=1000))
        factory.addStep(ShellCommand(doStepIf=getTag, workdir="build/yocto/meta-intel", command=["git", "checkout",  WithProperties("%s", "otherbranch")], timeout=1000))
        factory.addStep(ShellCommand(doStepIf=doEMGDTest, 
                        description="Copying EMGD", 
                        workdir="build",
                        # old. For bernard.
                        # command="cp -R /srv/www/vhosts/autobuilder/emgd_drivers/EMGD_1.6/* yocto/meta-intel/meta-" 
                        # + defaultenv['ABTARGET'] + "/recipes-graphics/xorg-xserver/", 
                        command="tar xvzf " + defaultenv['EMGD_DRIVER_DIR'] + "/emgd-driver-bin-1.8.tar.gz -C yocto/meta-intel",
                        timeout=600))
    elif provider=="fsl":
       factory.addStep(ShellCommand,
                       command="echo 'Checking out git://git.yoctoproject.org/meta-fsl-ppc.git'",
                       timeout=10)
       factory.addStep(ShellCommand(workdir="build/yocto/", command=["git", "clone",  "git://git.yoctoproject.org/meta-fsl-ppc.git"], timeout=1000))
       factory.addStep(ShellCommand(doStepIf=getTag, workdir="build/yocto/meta-fsl-ppc", command=["git", "checkout",  WithProperties("%s", "otherbranch")], timeout=1000))
    elif provider=="oe":
       factory.addStep(ShellCommand,
                       command="echo 'Checking out git://git.openembedded.org/meta-openembedded.git'",
                       timeout=10)
       factory.addStep(ShellCommand(workdir="build/yocto/", command=["git", "clone",  "git://git.openembedded.org/meta-openembedded.git"], timeout=1000))
       factory.addStep(ShellCommand(doStepIf=getTag, workdir="build/yocto/meta-openembedded", command=["git", "checkout",  WithProperties("%s", "otherbranch")], timeout=1000))

def runImage(factory, machine, image, distro, bsplayer, provider, buildhistory):
    factory.addStep(ShellCommand, description=["Setting up build"],
                    command=["yocto-autobuild-preamble"],
                    workdir="build", 
                    env=copy.copy(defaultenv),
                    timeout=14400)
    if distro.startswith("poky"):
        buildprovider="yocto"
    else:
        buildprovider="oe"
    createAutoConf(factory, btarget=machine, distro=distro, buildhistory=buildhistory)
    createBBLayersConf(factory, btarget=machine, bsplayer=bsplayer, provider=provider, buildprovider=buildprovider)
    defaultenv['MACHINE'] = machine
    factory.addStep(ShellCommand, description=["Building", machine, image],
                    command=["yocto-autobuild", image, "-k"],
                    env=copy.copy(defaultenv),
                    timeout=14400)

def runSanityTest(factory, machine, image):
    defaultenv['MACHINE'] = machine
    factory.addStep(ShellCommand, description=["Running sanity test for", 
                    machine, image], 
                    command=["yocto-autobuild-sanitytest", image], 
                    env=copy.copy(defaultenv), 
                    timeout=2400)
def getSlaveBaseDir(step):
    defaultenv['SLAVEBASEDIR'] = step.getProperty("SLAVEBASEDIR")
    return True

def getDest(step):
    defaultenv['DEST'] = step.getProperty("DEST")
    return True

def runPreamble(factory, target):
    factory.addStep(SetPropertiesFromEnv(variables=["SLAVEBASEDIR"]))
    factory.addStep(ShellCommand(doStepIf=getSlaveBaseDir,
                    env=copy.copy(defaultenv),
                    command='echo "Getting the slave basedir"'))
    factory.addStep(shell.SetProperty(
                    command="uname -a",
                    property="UNAME"))
    factory.addStep(shell.SetProperty(
                    command="echo $HOSTNAME",
                    property="HOSTNAME"))
    factory.addStep(ShellCommand(
                    description=["Building on", WithProperties("%s", "HOSTNAME"),  WithProperties("%s", "UNAME")],
                    command=["echo", WithProperties("%s", "HOSTNAME"),  WithProperties("%s", "UNAME")]))
    factory.addStep(ShellCommand(doStepIf=getCleanSS,
                description="Prepping for nightly creation by removing SSTATE", 
                timeout=62400,
                command=["rm", "-rf", defaultenv['SSTATE_DIR'], defaultenv['LSB_SSTATE_DIR']]))
    factory.addStep(setDest(workdir=WithProperties("%s", "workdir"), btarget=target))
    factory.addStep(ShellCommand(doStepIf=getRepo,
                    description="Getting the requested git repo",
                    command='echo "Getting the requested git repo"'))
    factory.addStep(shell.SetProperty(workdir="build/meta-qt3",
                    command="git rev-parse HEAD",
                    property="QTHASH"))
    factory.addStep(ShellCommand(doStepIf=doNightlyArchTest,
                    description="Syncing Local Build History Repo",
                    workdir=defaultenv['BUILD_HISTORY_DIR'] + "/" + defaultenv['ABTARGET'] + "/poky-buildhistory",
                    command=["git", "pull", "origin", defaultenv['ABTARGET']],
                    timeout=2000))

def getRepo(step):
    gittype = step.getProperty("repository")
    if gittype == "git://git.yoctoproject.org/poky-contrib":
        step.setProperty("otherbranch", "master")
    elif gittype == "git://git.yoctoproject.org/poky":
        try:
            branch = step.getProperty("branch")
            if branch != "master":
                step.setProperty("otherbranch", branch)
            else:
                step.setProperty("otherbranch", "master")
        except: 
            step.setProperty("branch", "master")
            step.setProperty("otherbranch", "master")
            pass
    else:
        return False
    defaultenv['BRANCH']=step.getProperty("otherbranch")
    return True

def getTag(step):
    try:
        tag = step.getProperty("pokytag")
    except:
        step.setProperty("pokytag", "HEAD")
        pass
    return True

def makeCheckout(factory):
    factory.addStep(ShellCommand(doStepIf=getRepo,
                    description="Getting the requested git repo",
                    command='echo "Getting the requested git repo"'))
    factory.addStep(Git(
                    mode="clobber", 
                    branch=WithProperties("%s", "branch"),
                    timeout=10000, retry=(5, 3)))
    factory.addStep(ShellCommand(doStepIf=getTag, command=["git", "checkout",  WithProperties("%s", "pokytag")], timeout=1000))
    factory.addStep(ShellCommand(workdir="build", command=["git", "clone",  "git://git.yoctoproject.org/meta-qt3.git"], timeout=1000))
    factory.addStep(ShellCommand(doStepIf=getTag, workdir="build/meta-qt3", command=["git", "checkout",  WithProperties("%s", "otherbranch")], timeout=1000))
    factory.addStep(shell.SetProperty(workdir="build/meta-qt3",
                    command="git rev-parse HEAD",
                    property="QTHASH"))
    factory.addStep(ShellCommand(
                    description=["Building", WithProperties("%s", "branch"),  WithProperties("%s", "repository")],
                    command=["echo", WithProperties("%s", "branch"),  WithProperties("%s", "repository")]))

                    
def makeTarball(factory):
    factory.addStep(ShellCommand, description="Generating release tarball", 
                    command=["yocto-autobuild-generate-sources-tarball", "nightly", "1.1pre", 
                    WithProperties("%s", "branch")], timeout=120)
    publishArtifacts(factory, "tarball", "build/build/tmp")


def makeLayerTarball(factory):
    factory.addStep(ShellCommand, description="Generating release tarball",
                    command=["yocto-autobuild-generate-sources-tarball", "nightly", "1.1pre",
                    WithProperties("%s", "layer0branch")], timeout=120)
    publishArtifacts(factory, "layer-tarball", "build/build/tmp")

def doEMGDTest(step):
    buildername = step.getProperty("buildername")
    branch = step.getProperty("otherbranch")
    if "edison" in branch and (buildername == "crownbay" or buildername == "fri2"):
        return True
    else:
        return False 

def setRandom(step):
    step.setProperty("FuzzArch", random.choice( ['qemux86', 
                                                 'qemux86-64', 
                                                 'qemuarm', 
                                                 'qemuppc', 
                                                 'qemumips'] ))
    step.setProperty("FuzzImage", random.choice( ['core-image-sato', 
                                                  'core-image-sato-dev', 
                                                  'core-image-sato-sdk', 
                                                  'core-image-minimal', 
                                                  'core-image-minimal-dev',
                                                  'core-image-lsb', 
                                                  'core-image-lsb-dev', 
                                                  'core-image-lsb-sdk', 
                                                  'core-image-lsb-qt3']))
    step.setProperty("FuzzSDK", random.choice( ['i686', 'x86-64'] ))
    imageType = step.getProperty("FuzzImage")
    defaultenv['FuzzSDK'] = step.getProperty("FuzzSDK")
    defaultenv['FuzzImage'] = step.getProperty("FuzzImage")
    defaultenv['FuzzArch'] = step.getProperty("FuzzArch")
    if imageType.endswith("lsb"):
        step.setProperty("distro", "poky-lsb")  
    else:
        step.setProperty("distro", "poky")
    return True

def fuzzyBuild(factory):
    factory.addStep(ShellCommand(doStepIf=setRandom,
                    description="Setting to random build parameters",
                    command='echo "Setting to random build parameters"'))
    factory.addStep(ShellCommand(doStepIf=setRandom,
                    description=["Building", WithProperties("%s", "FuzzImage"),  
                                 WithProperties("%s", "FuzzArch"), 
                                 WithProperties("%s", "FuzzSDK")],
                    command=["echo", WithProperties("%s", "FuzzImage"),  
                             WithProperties("%s", "FuzzArch"), 
                             WithProperties("%s", "FuzzSDK")],
                     env=copy.copy(defaultenv)))                                   
    runPreamble(factory, defaultenv["FuzzArch"])
    createAutoConf(factory, btarget=defaultenv["FuzzArch"], distro=defaultenv["FuzzImage"])
    createBBLayersConf(factory, btarget=defaultenv["FuzzArch"], bsplayer=False, provider="intel")
    factory.addStep(ShellCommand, 
                    description=["Building", WithProperties("%s", "FuzzImage")],
                    command=["yocto-autobuild", 
                             WithProperties("%s", "FuzzImage"), "-k"],
                    env=copy.copy(defaultenv),
                    timeout=14400)

def getMetaParams(step):
    defaultenv['MACHINE'] = step.getProperty("machine")
    defaultenv['SDKMACHINE'] = step.getProperty("sdk")
    step.setProperty("MetaImage", step.getProperty("imagetype").replace("and", " "))
    return True

def getCleanSS(step):
    try:
        cleansstate = step.getProperty("cleansstate")
    except:
        cleansstate = False
    if cleansstate=="True":
        return True
    else:
        return False

def metaBuild(factory):
    defaultenv['IMAGETYPES'] = ""
    defaultenv['SDKMACHINE'] = ""
    factory.addStep(ShellCommand(doStepIf=getMetaParams,
                    description="Getting to meta build parameters",
                    command='echo "Getting to meta build parameters"'))
    runPreamble(factory, WithProperties("%s", "machine"))
    factory.addStep(ShellCommand, description=["Setting up build"],
                    command=["yocto-autobuild-preamble"],
                    workdir="build", 
                    env=copy.copy(defaultenv),
                    timeout=14400)                                                 
    createAutoConf(factory, btarget=defaultenv["machine"], distro="poky")
    createBBLayersConf(factory, btarget=defaultenv["machine"], bsplayer=False, provider="intel")
    factory.addStep(ShellCommand, description=["Building", WithProperties("%s", "MetaImage")],
                    command=["yocto-autobuild", WithProperties("%s", "MetaImage"), "-k"],
                    env=copy.copy(defaultenv),
                    timeout=14400)

def nightlyQEMU(factory, machine, distrotype, provider):
    if distrotype == "poky":
        defaultenv['DISTRO'] = "poky"
        runImage(factory, machine, 'core-image-sato core-image-sato-dev core-image-sato-sdk core-image-minimal core-image-minimal-dev', distrotype, False, provider, defaultenv['BUILD_HISTORY_COLLECT'])
        publishArtifacts(factory, machine, "build/build/tmp")
        publishArtifacts(factory, "ipk", "build/build/tmp")
        publishArtifacts(factory, "rpm", "build/build/tmp")
        runSanityTest(factory, machine, 'core-image-sato')
        runSanityTest(factory, machine, 'core-image-minimal')
    elif distrotype == "poky-lsb":
        defaultenv['DISTRO'] = "poky-lsb"
        runImage(factory, machine, 'core-image-lsb core-image-lsb-dev core-image-lsb-sdk core-image-lsb-qt3', distrotype, False, provider, False)
        publishArtifacts(factory, machine, "build/build/tmp")
        publishArtifacts(factory, "ipk", "build/build/tmp")
        publishArtifacts(factory, "rpm", "build/build/tmp")
    defaultenv['DISTRO'] = 'poky'

def nightlyBSP(factory, machine, distrotype, provider):
    if distrotype == "poky":
        defaultenv['DISTRO'] = 'poky'
        runImage(factory, machine, 'core-image-sato core-image-sato-sdk core-image-minimal', distrotype, False, provider, False)
        publishArtifacts(factory, machine, "build/build/tmp")
        publishArtifacts(factory, "ipk", "build/build/tmp")
        publishArtifacts(factory, "rpm", "build/build/tmp")
    elif distrotype == "poky-lsb":
        defaultenv['DISTRO'] = 'poky-lsb'
        runImage(factory, machine,  'core-image-lsb-qt3 core-image-lsb-sdk', distrotype, False, provider, False)
        publishArtifacts(factory, machine, "build/build/tmp")
        publishArtifacts(factory, "ipk", "build/build/tmp")
        publishArtifacts(factory, "rpm", "build/build/tmp")
    defaultenv['DISTRO'] = 'poky'
                   
def setBSPLayerRepo(step):
####################
# WIP web selectable layer support
####################
    defaultenv['BSP_REPO'] = step.getProperty("layer0repo")
    defaultenv['BSP_BRANCH'] = step.getProperty("layer0branch")
    defaultenv['BSP_WORKDIR'] = "build/" + step.getProperty("layer0workdir")
    defaultenv['BSP_REV'] = step.getProperty("layer0revision")
    return True

def runPostamble(factory):
    factory.addStep(ShellCommand(description=["Setting destination"],
                    command=["sh", "-c", WithProperties('echo "%s" > ./deploy-dir', "DEST")],
                    env=copy.copy(defaultenv),
                    timeout=14400))
    if PUBLISH_BUILDS == "True":
        factory.addStep(ShellCommand, description="Creating CURRENT link",
                        command=["sh", "-c", WithProperties("rm -rf %s/../CURRENT; ln -s %s %s/../CURRENT", "DEST", "DEST", "DEST")],
                        timeout=20)
        factory.addStep(ShellCommand(
                        description="Making tarball dir",
                        command=["mkdir", "-p", "yocto"],
                        env=copy.copy(defaultenv),
                        timeout=14400))
        factory.addStep(ShellCommand, description="Grabbing git archive",
                        command=["sh", "-c", WithProperties("git archive `echo '%s'|sed 's/\//:/g'` | tar -x -C yocto", "otherbranch")],
                        timeout=600)
        factory.addStep(ShellCommand, description="Creating tarball",
                        command=["sh", "-c", "tar cvjf yocto.tar.bz2 yocto"],
                        timeout=600)
        factory.addStep(ShellCommand, description="Moving tarball", 
                        command=["sh", "-c", WithProperties("mv yocto.tar.bz2 %s", "DEST")],
                        timeout=600)

def buildBSPLayer(factory, distrotype, btarget, provider):
    if distrotype == "poky":
        defaultenv['DISTRO'] = 'poky'
        runImage(factory, btarget, 'core-image-sato core-image-sato-sdk core-image-minimal', distrotype, True, provider, False)
        publishArtifacts(factory, defaultenv['ABTARGET'], "build/build/tmp")
        publishArtifacts(factory, "ipk", "build/build/tmp")
        publishArtifacts(factory, "rpm", "build/build/tmp")
    elif distrotype == "poky-lsb":
        defaultenv['DISTRO'] = 'poky-lsb'
        runImage(factory, btarget, 'core-image-lsb core-image-lsb-sdk', distrotype, True, provider, False)
        publishArtifacts(factory, defaultenv['ABTARGET'], "build/build/tmp")
        publishArtifacts(factory, "ipk", "build/build/tmp")
        publishArtifacts(factory, "rpm", "build/build/tmp")
    defaultenv['DISTRO'] = 'poky'

def publishArtifacts(factory, artifact, tmpdir):
    factory.addStep(ShellCommand(description=["Setting destination"],
                    command=["sh", "-c", WithProperties('echo "%s" > ./deploy-dir', "DEST")],
                    env=copy.copy(defaultenv),
                    timeout=14400))
    factory.addStep(shell.SetProperty(workdir="build",
                        command="echo " + artifact,
                        property="ARTIFACT"))

    if PUBLISH_BUILDS == "True":
        if artifact == "adt_installer":
            factory.addStep(ShellCommand(
                            description="Making adt_installer dir",
                            command=["mkdir", "-p", WithProperties("%s/adt_installer", "DEST")],
                            env=copy.copy(defaultenv),
                            timeout=14400))
            factory.addStep(ShellCommand(
                            description=["Copying adt_installer"],
                            command=["sh", "-c", WithProperties("cp -R *adt* %s/adt_installer", "DEST")],
                            workdir=tmpdir + "/deploy/sdk",
                            env=copy.copy(defaultenv),
                            timeout=14400))
        elif artifact == "toolchain":
            factory.addStep(ShellCommand(
                            description="Making toolchain deploy dir",
                            command=["mkdir", "-p", WithProperties("%s/toolchain/i686", "DEST")],
                            env=copy.copy(defaultenv),
                            timeout=14400))
            factory.addStep(ShellCommand(
                            description=["Copying i686 toolchain"],
                            command=["sh", "-c", WithProperties("cp -Rd *i686* %s/toolchain/i686", "DEST")],
                            workdir=tmpdir + "/deploy/sdk",
                            env=copy.copy(defaultenv), 
                            timeout=14400))
            factory.addStep(ShellCommand(
                            description=["Making toolchain deploy dir"],
                            command=["mkdir", '-p', WithProperties("%s/toolchain/x86-64", "DEST")],
                            env=copy.copy(defaultenv), 
                            timeout=14400))
            factory.addStep(ShellCommand(
                            description=["Copying x86-64 toolchain"],
                            command=["sh", "-c", WithProperties("cp -Rd *x86_64* %s/toolchain/x86-64", "DEST")],
                            workdir=tmpdir + "/deploy/sdk", 
                            env=copy.copy(defaultenv),
                            timeout=14400))          

        elif artifact.startswith("qemu"):
            if artifact == "qemux86-tiny":
                factory.addStep(ShellCommand(
                                description=["Making " + artifact + " deploy dir"],
                                command=["mkdir", "-p", WithProperties("%s/machines/qemu/%s", "DEST", "ARTIFACT")],
                                env=copy.copy(defaultenv),
                                timeout=14400))
                factory.addStep(ShellCommand(
                                description=["Copying " + artifact + " artifacts"],
                                command=["sh", "-c", WithProperties("cp -Rd *%s* %s/machines/qemu/qemux86-tiny", 'ARTIFACT', 'DEST')],
                                workdir=tmpdir + "/deploy/images",
                                env=copy.copy(defaultenv),
                                timeout=14400))
            else:
                factory.addStep(ShellCommand(
                                description=["Making " + artifact + " deploy dir"],
                                command=["mkdir", "-p", WithProperties("%s/machines/qemu/%s", "DEST", "ARTIFACT")],
                                env=copy.copy(defaultenv),
                                timeout=14400))
                factory.addStep(ShellCommand(
                                description=["Copying " + artifact + " artifacts"],
                                command=["sh", "-c", WithProperties("cp -Rd *%s* %s/machines/qemu/%s", 'ARTIFACT', 'DEST', 'ARTIFACT')],
                                workdir=tmpdir + "/deploy/images",
                                env=copy.copy(defaultenv),
                                timeout=14400))
        else:
            factory.addStep(ShellCommand( 
                            description=["Making " + artifact + " deploy dir"],
                            command=["mkdir", "-p", WithProperties("%s/machines/%s", "DEST", "ARTIFACT")],
                            env=copy.copy(defaultenv), 
                            timeout=14400))
            factory.addStep(ShellCommand(
                            description=["Copying " + artifact + " artifacts"],
                            command=["sh", "-c", WithProperties("cp -Rd *%s* %s/machines/%s", 'ARTIFACT', 'DEST', 'ARTIFACT')],
                            workdir=tmpdir + "/deploy/images", 
                            env=copy.copy(defaultenv),
                            timeout=14400))          

######################################################################
#
# Do not use tmp copy. They're there for debugging only. They really do make
# a mess of things.
#
######################################################################
        if artifact == "non-lsb-tmp":
            factory.addStep(ShellCommand( 
                            description=["Making " +artifact + " deploy dir"],
                            command=["mkdir", "-p", WithProperties("%s/tmp", "DEST")],
                            env=copy.copy(defaultenv),
                            timeout=14400))
            factory.addStep(ShellCommand( 
                            description=["Copying non-lsb tmp dir"],
                            command=["sh", "-c", WithProperties("cp -Rd * %s/tmp", "DEST")],
                            workdir=tmpdir, 
                            env=copy.copy(defaultenv),
                            timeout=14400))                           
                
        if artifact == "lsb-tmp":       
            factory.addStep(ShellCommand( 
                            description=["Making " + artifact + " deploy dir"],
                            command=["mkdir", "-p", WithProperties("%s/lsb-tmp", "DEST")],
                            env=copy.copy(defaultenv),
                            timeout=14400))
            factory.addStep(ShellCommand, description=["Copying non-lsb tmp dir"],
                            command=["sh", "-c", WithProperties("cp -Rd * %s/lsb-tmp", "DEST")],
                            workdir=tmpdir, 
                            env=copy.copy(defaultenv),
                            timeout=14400)                           
            
        if artifact == "rpm" or artifact == "deb" or artifact == "ipk":        
            factory.addStep(ShellCommand, description=["Copying " + artifact],
                    command=["sh", "-c", WithProperties("rsync -av %s %s", 'ARTIFACT', 'DEST')],
                    workdir=tmpdir + "/deploy/", 
                    env=copy.copy(defaultenv),
                    timeout=14400)
            
        if artifact == "buildstats":
            PKGDIR = os.path.join(DEST, artifact)
            factory.addStep(ShellCommand( 
                            description=["Making " + artifact + " deploy dir"],
                            command=["mkdir", "-p", WithProperties("%s/buildstats", "DEST")],
                            env=copy.copy(defaultenv),
                            timeout=14400))
            factory.addStep(ShellCommand, description=["Copying " + artifact],
                            command=["sh", "-c", WithProperties("rsync -av * %s/buildstats", "DEST")],
                            workdir=tmpdir + "/buildstats", 
                            env=copy.copy(defaultenv),
                            timeout=14400)   
            
    if PUBLISH_SSTATE == "True" and artifact == "sstate":
        factory.addStep(ShellCommand, description="Syncing shared state cache to mirror", 
                        command="yocto-update-shared-state-prebuilds", timeout=2400)

################################################################################
#
# BuildSets Section
# These are predefined buildsets used on the yocto-project production autobuilder
#
################################################################################

################################################################################
#
# Nightly Release Builder
#
################################################################################
f65 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f65)
runPreamble(f65, defaultenv['ABTARGET'])
runImage(f65, 'qemux86', 'universe -c fetch', "poky", False, "yocto", False)

f65.addStep(Trigger(schedulerNames=['nightly-x86'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f65.addStep(Trigger(schedulerNames=['nightly-x86-64'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f65.addStep(Trigger(schedulerNames=['nightly-arm'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f65.addStep(Trigger(schedulerNames=['nightly-ppc'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f65.addStep(Trigger(schedulerNames=['nightly-mips'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f65.addStep(Trigger(schedulerNames=['eclipse-plugin'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f65.addStep(YoctoBlocker(idlePolicy="block", timeout=62400, upstreamSteps=[("nightly-arm", "nightly"),
                                        ("nightly-x86", "nightly"),
                                        ("nightly-x86-64", "nightly"),
                                        ("nightly-mips", "nightly"),
                                        ("nightly-ppc", "nightly")]))
runPostamble(f65)
f65.addStep(ShellCommand, 
            description="Prepping for package-index creation by copying ipks back to main builddir", workdir="build/build/tmp/deploy",
            command=["sh", "-c", WithProperties("cp -R %s/ipk ipk", "DEST")])
f65.addStep(ShellCommand,
            description="Prepping for package-index creation by copying rpms back to main builddir", workdir="build/build/tmp/deploy",
            command=["sh", "-c", WithProperties("cp -R %s/rpm rpm", "DEST")])
defaultenv['SDKMACHINE'] = 'i686'
runImage(f65, 'qemux86', 'package-index', "poky", False, "yocto", False)
defaultenv['SDKMACHINE'] = 'x86_64'
runImage(f65, 'qemux86', 'package-index', "poky", False, "yocto", False)
publishArtifacts(f65, "ipk", "build/build/tmp")
publishArtifacts(f65, "rpm", "build/build/tmp")
runImage(f65, 'qemux86', 'adt-installer', "poky", False, "yocto", False)
publishArtifacts(f65, "adt_installer", "build/build/tmp")
b65 = {'name': "nightly",
      'slavenames': ["builder1"],
      'builddir': "nightly",
      'factory': f65
      }
yocto_builders.append(b65)

yocto_sched.append(triggerable.Triggerable(name="nightly-x86", builderNames=["nightly-x86"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-x86-64", builderNames=["nightly-x86-64"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-arm", builderNames=["nightly-arm"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-ppc", builderNames=["nightly-ppc"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-mips", builderNames=["nightly-mips"]))
yocto_sched.append(triggerable.Triggerable(name="eclipse-plugin", builderNames=["eclipse-plugin"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-world", builderNames=["nightly-world"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-multilib", builderNames=["nightly-multilib"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-non-gpl3", builderNames=["nightly-non-gpl3"]))
yocto_sched.append(triggerable.Triggerable(name="nightly-tiny", builderNames=["nightly-tiny"]))

################################################################################
#
# Eclipse Plugin Builder
#
# This builds the eclipse plugin. This is a temporary area until this
# gets merged into the nightly & milestone builds
#
################################################################################

f61 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'eclipse-plugin'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
runPreamble(f61, defaultenv['ABTARGET'])
f61.addStep(ShellCommand, description="cleaning up eclipse build dir",
			command="rm -rf *",
			workdir=WithProperties("%s", "workdir"))
f61.addStep(ShellCommand, description="Cloning eclipse-poky git repo",
            command="yocto-eclipse-plugin-clone-repo", timeout=300)
f61.addStep(ShellCommand, description="Checking out Eclipse Master Branch",
            workdir="build/eclipse-plugin",
            command="git checkout master",
            timeout=600)
f61.addStep(ShellCommand, description="Building eclipse plugin",
            workdir="build/eclipse-plugin/scripts",
            command="./setup.sh",
            timeout=6000)
f61.addStep(ShellCommand, description="Building eclipse plugin",
            workdir="build/eclipse-plugin/scripts",
            command="ECLIPSE_HOME=/srv/home/pokybuild/yocto-autobuilder/yocto-slave/eclipse-plugin/build/eclipse-plugin/scripts/eclipse ./build.sh master rc1",
            timeout=6000)
if PUBLISH_BUILDS == "True":
    f61.addStep(ShellCommand(
                description=["Making eclipse deploy dir"],
                command=["mkdir", "-p", WithProperties("%s/eclipse-plugin/indigo", "DEST")],
                env=copy.copy(defaultenv),
                timeout=14400))
    f61.addStep(ShellCommand, description=["Copying eclipse-plugin dir"],
                command=["sh", "-c", WithProperties("cp *.zip %s/eclipse-plugin/indigo", "DEST")],
                workdir="build/eclipse-plugin/scripts",
                env=copy.copy(defaultenv),
                timeout=14400)
b61 = {'name': "eclipse-plugin",
      'slavenames': ["builder1", "builder1",  "builder1"],
      'builddir': "eclipse-plugin",
      'factory': f61,
      }
yocto_builders.append(b61)

################################################################################
#
# Nightly x86
#
################################################################################
f66 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-x86'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f66)
runPreamble(f66, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f66.addStep(ShellCommand, description="Setting SDKMACHINE=i686",
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
nightlyQEMU(f66, 'qemux86', 'poky', "yocto")
nightlyBSP(f66, 'atom-pc', 'poky', "yocto")
runImage(f66, 'qemux86', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
defaultenv['SDKMACHINE'] = 'x86_64'
f66.addStep(ShellCommand, description="Setting SDKMACHINE=x86_64", 
            command="echo 'Setting SDKMACHINE=x86_64'", timeout=10)
runImage(f66, 'qemux86', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
publishArtifacts(f66, "toolchain", "build/build/tmp")
publishArtifacts(f66, "ipk", "build/build/tmp")
f66.addStep(ShellCommand, description="Moving non-lsb TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
defaultenv['DISTRO'] = "poky-lsb"
nightlyQEMU(f66, 'qemux86', "poky-lsb", "yocto")
nightlyBSP(f66, 'atom-pc', 'poky-lsb', "yocto")
f66.addStep(NoOp(name="nightly"))
b66 = {'name': "nightly-x86",
      'slavenames': ["builder1",  "builder1"], 
      'builddir': "nightly-x86",
      'factory': f66,
      }
yocto_builders.append(b66)

################################################################################
#
# Nightly x86-64
#
################################################################################
f67 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-x86-64'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f67)
runPreamble(f67, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f67.addStep(ShellCommand, description="Setting SDKMACHINE=i686", 
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
nightlyQEMU(f67, 'qemux86-64', 'poky', "yocto")
runImage(f67, 'qemux86-64', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
defaultenv['SDKMACHINE'] = 'x86_64'
f67.addStep(ShellCommand, description="Setting SDKMACHINE=x86_64", 
            command="echo 'Setting SDKMACHINE=x86_64'", timeout=10)
runImage(f67, 'qemux86-64', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
publishArtifacts(f67, "toolchain","build/build/tmp")
publishArtifacts(f67, "ipk", "build/build/tmp")
f67.addStep(ShellCommand, description="Moving non-lsb TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
nightlyQEMU(f67, 'qemux86-64', "poky-lsb", "yocto")
f67.addStep(NoOp(name="nightly"))
b67 = {'name': "nightly-x86-64",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "nightly-x86-64",
      'factory': f67,
      }
yocto_builders.append(b67)

################################################################################
#
# Nightly arm
#
################################################################################
f68 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-arm'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f68)
runPreamble(f68, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f68.addStep(ShellCommand, description="Setting SDKMACHINE=i686", 
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
nightlyQEMU(f68, 'qemuarm', 'poky', "yocto")
nightlyBSP(f68, 'beagleboard', 'poky', "yocto")
runImage(f68, 'qemuarm', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
defaultenv['SDKMACHINE'] = 'x86_64'
f68.addStep(ShellCommand, description="Setting SDKMACHINE=x86_64", 
            command="echo 'Setting SDKMACHINE=x86_64'", timeout=10)
runImage(f68, 'qemuarm', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
publishArtifacts(f68, "toolchain","build/build/tmp")
publishArtifacts(f68, "ipk", "build/build/tmp")
f68.addStep(ShellCommand, description="Moving non-lsb TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
nightlyQEMU(f68, 'qemuarm', "poky-lsb", "yocto")
nightlyBSP(f68, 'beagleboard', 'poky-lsb', "yocto")
f68.addStep(NoOp(name="nightly"))
b68 = {'name': "nightly-arm",
      'slavenames': ["builder1", "builder1"],
      'builddir': "nightly-arm",
      'factory': f68,
      }
yocto_builders.append(b68)

################################################################################
#
# Nightly mips
#
################################################################################
f69 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-mips'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f69)
runPreamble(f69, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f69.addStep(ShellCommand, description="Setting SDKMACHINE=i696", 
            command="echo 'Setting SDKMACHINE=i696'", timeout=10)
nightlyQEMU(f69, 'qemumips', 'poky', "yocto")
nightlyBSP(f69, 'routerstationpro', 'poky', "yocto")
runImage(f69, 'qemumips', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
defaultenv['SDKMACHINE'] = 'x86_64'
f69.addStep(ShellCommand, description="Setting SDKMACHINE=x86_64", 
            command="echo 'Setting SDKMACHINE=x86_64'", timeout=10)
runImage(f69, 'qemumips', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
publishArtifacts(f69, "toolchain", "build/build/tmp" )
publishArtifacts(f69, "ipk", "build/build/tmp")
f69.addStep(ShellCommand, description="Moving non-lsb TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
nightlyQEMU(f69, 'qemumips', "poky-lsb", "yocto")
nightlyBSP(f69, 'routerstationpro', 'poky-lsb', "yocto")
f69.addStep(NoOp(name="nightly"))
b69 = {'name': "nightly-mips",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "nightly-mips",
      'factory': f69,
      }
yocto_builders.append(b69)


################################################################################
#
# Nightly ppc
#
################################################################################
f70 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-ppc'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f70)
runPreamble(f70, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f70.addStep(ShellCommand, description="Setting SDKMACHINE=i686", 
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
nightlyQEMU(f70, 'qemuppc', 'poky', 'yocto')
nightlyBSP(f70, 'mpc8315e-rdb', 'poky', 'yocto')
runImage(f70, 'qemuppc', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
defaultenv['SDKMACHINE'] = 'x86_64'
f70.addStep(ShellCommand, description="Setting SDKMACHINE=x86_64", 
            command="echo 'Setting SDKMACHINE=x86_64'", timeout=10)
runImage(f70, 'qemuppc', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "yocto", defaultenv['BUILD_HISTORY_COLLECT'])
publishArtifacts(f70, "toolchain", "build/build/tmp")
publishArtifacts(f70, "ipk", "build/build/tmp")
f70.addStep(ShellCommand, description="Moving non-lsb TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
nightlyQEMU(f70, 'qemuppc', 'poky-lsb', 'yocto')
nightlyBSP(f70, 'mpc8315e-rdb', 'poky-lsb' , 'yocto')
f70.addStep(NoOp(name="nightly"))
b70 = {'name': "nightly-ppc",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "nightly-ppc",
      'factory': f70,
      }
yocto_builders.append(b70)


################################################################################
#
# Nightly world
#
################################################################################
f75 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-world'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f75)
runPreamble(f75, defaultenv['ABTARGET'])
f75.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f75)
runPreamble(f75, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f75.addStep(ShellCommand, description="Setting SDKMACHINE=i686",
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
runImage(f75, 'qemux86', 'world', defaultenv['DISTRO'], False, "yocto", False)
f75.addStep(NoOp(name="nightly"))
b75 = {'name': "nightly-world",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "nightly-world",
      'factory': f75
      }
yocto_builders.append(b75)


################################################################################
#
# Nightly nonGPLv3
#
################################################################################
f80 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-non-gpl3'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f80)
runPreamble(f80, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f80.addStep(ShellCommand, description="Setting SDKMACHINE=i686",
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
runImage(f80, 'qemux86', 'core-image-minimal core-image-basic', defaultenv['DISTRO'], False, "yocto", False)
f80.addStep(NoOp(name="nightly"))
b80 = {'name': "nightly-non-gpl3",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "nightly-non-gpl3",
      'factory': f80
      }
yocto_builders.append(b80)

################################################################################
#
# Nightly multilib
#
################################################################################
f90 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-multilib'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f90)
runPreamble(f90, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'x86_64'
f90.addStep(ShellCommand, description="Setting SDKMACHINE=x86_64",
            command="echo 'Setting SDKMACHINE=x86_64'", timeout=10)
runImage(f90, 'qemux86-64', 'lib32-core-image-minimal', defaultenv['DISTRO'], False, "yocto", False)
publishArtifacts(f90, "qemu","build/build/tmp")
f90.addStep(NoOp(name="nightly"))
b90 = {'name': "nightly-multilib",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "nightly-multilib",
      'factory': f90
      }
yocto_builders.append(b90)

################################################################################
#
# Nightly tiny
#
################################################################################
f95 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky-tiny'
defaultenv['ABTARGET'] = 'nightly-tiny'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f95)
runPreamble(f95, defaultenv['ABTARGET'])
f95.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f95)
runPreamble(f95, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
f95.addStep(ShellCommand, description="Setting SDKMACHINE=i686",
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
runImage(f95, 'qemux86', 'core-image-minimal', defaultenv['DISTRO'], False, "yocto", False)
publishArtifacts(f95, "qemux86-tiny","build/build/tmp")
f95.addStep(NoOp(name="nightly"))
b95 = {'name': "nightly-tiny",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "nightly-tiny",
      'factory': f95
      }
yocto_builders.append(b95)

################################################################################
#
# Nightly Release Builder
#
################################################################################
f100 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'nightly-meta-intel'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
makeCheckout(f100)
runPreamble(f100, defaultenv['ABTARGET'])
runImage(f100, 'qemux86', 'universe -c fetch', "poky", False, "yocto", False)

f100.addStep(Trigger(schedulerNames=['crownbay'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['crownbay-noemgd'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['fri2'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['fri2-noemgd'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['emenlow'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['cedartrail'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['jasperforest'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['n450'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['sugarbay'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))
f100.addStep(Trigger(schedulerNames=['romley'],
                            updateSourceStamp=False,
                            set_properties={'DEST': Property("DEST")},
                            waitForFinish=False))

f100.addStep(YoctoBlocker(idlePolicy="block", timeout=62400, upstreamSteps=[
                                        ("crownbay", "nightly-meta-intel"),
                                        ("crownbay-noemgd", "nightly-meta-intel"),
                                        ("fri2", "nightly-meta-intel"),
                                        ("fri2-noemgd", "nightly-meta-intel"),
                                        ("emenlow", "nightly-meta-intel"),
                                        ("cedartrail", "nightly-meta-intel"),
                                        ("jasperforest", "nightly-meta-intel"),
                                        ("n450", "nightly-meta-intel"),
                                        ("romley", "nightly-meta-intel"),
                                        ("sugarbay", "nightly-meta-intel")]))
runPostamble(f100)
b100 = {'name': "nightly-meta-intel",
      'slavenames': ["builder1"],
      'builddir': "nightly-meta-intel",
      'factory': f100
      }
yocto_builders.append(b100)

yocto_sched.append(triggerable.Triggerable(name="crownbay", builderNames=["crownbay"]))
yocto_sched.append(triggerable.Triggerable(name="crownbay-noemgd", builderNames=["crownbay-noemgd"]))
yocto_sched.append(triggerable.Triggerable(name="fri2-noemgd", builderNames=["fri2-noemgd"]))
yocto_sched.append(triggerable.Triggerable(name="fri2", builderNames=["fri2"]))
yocto_sched.append(triggerable.Triggerable(name="emenlow", builderNames=["emenlow"]))
yocto_sched.append(triggerable.Triggerable(name="cedartrail", builderNames=["cedartrail"]))
yocto_sched.append(triggerable.Triggerable(name="jasperforest", builderNames=["jasperforest"]))
yocto_sched.append(triggerable.Triggerable(name="n450", builderNames=["n450"]))
yocto_sched.append(triggerable.Triggerable(name="sugarbay", builderNames=["sugarbay"]))
yocto_sched.append(triggerable.Triggerable(name="romley", builderNames=["romley"]))

#####################################################################
#
# Crownbay Buildout
#
#####################################################################
f170 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'crownbay'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'crownbay'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f170.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f170)
runPreamble(f170, defaultenv['ABTARGET'])
runBSPLayerPreamble(f170, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f170, "poky", defaultenv['ABTARGET'], "intel")
f170.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f170, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f170)
f170.addStep(NoOp(name="nightly-meta-intel"))
b170 = {'name': "crownbay",
       'slavenames': ["builder1", "builder1"],
       'builddir': "crownbay",
       'factory': f170}
yocto_builders.append(b170)

#####################################################################
#
# Crownbay-noemgd Buildout
#
#####################################################################

f175 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'crownbay-noemgd'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'crownbay'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f175.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f175)
runPreamble(f175, defaultenv['ABTARGET'])
runBSPLayerPreamble(f175, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f175, "poky", defaultenv['ABTARGET'], "intel")
f175.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f175, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f175)
f175.addStep(NoOp(name="nightly-meta-intel"))
b175 = {'name': "crownbay-noemgd",
       'slavenames': ["builder1", "builder1"],
       'builddir': "crownbay-noemgd",
       'factory': f175}
yocto_builders.append(b175)

#####################################################################
#
# Emenlow Buildout
#
#####################################################################
f180 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'emenlow'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'emenlow'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f180.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f180)
runPreamble(f180, defaultenv['ABTARGET'])
runBSPLayerPreamble(f180, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f180, "poky", defaultenv['ABTARGET'], "intel")
f180.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f180, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f180)
f180.addStep(NoOp(name="nightly-meta-intel"))
b180 = {'name': "emenlow",
       'slavenames': ["builder1", "builder1"],
       'builddir': "emenlow",
       'factory': f180}
yocto_builders.append(b180)

#####################################################################
#
# n450 Buildout
#
#####################################################################
f190 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'n450'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'n450'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f190.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f190)
runPreamble(f190, defaultenv['ABTARGET'])
runBSPLayerPreamble(f190, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f190, "poky", defaultenv['ABTARGET'], "intel")
f190.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f190, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f190)
f190.addStep(NoOp(name="nightly-meta-intel"))
b190= {'name': "n450",
      'slavenames': ["builder1", "builder1"],
       'builddir': "n450",
       'factory': f190}
yocto_builders.append(b190)

#####################################################################
#
# jasperforest Buildout
#
#####################################################################
f200 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'jasperforest'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'jasperforest'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f200.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f200)
runPreamble(f200, defaultenv['ABTARGET'])
runBSPLayerPreamble(f200, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f200, "poky", defaultenv['ABTARGET'], "intel")
f200.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f200, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f200)
f200.addStep(NoOp(name="nightly-meta-intel"))
b200 = {'name': "jasperforest",
       'slavenames': ["builder1", "builder1"],
       'builddir': "jasperforest",
       'factory': f200}
yocto_builders.append(b200)

#####################################################################
#
# Sugarbay Buildout
#
#####################################################################
f210 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'sugarbay'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'sugarbay'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f210.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f210)
runPreamble(f210, defaultenv['ABTARGET'])
runBSPLayerPreamble(f210, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f210, "poky", defaultenv['ABTARGET'], "intel")
f210.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f210, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f210)
f210.addStep(NoOp(name="nightly-meta-intel"))
b210 = {'name': "sugarbay",
       'slavenames': ["builder1", "builder1"],
       'builddir': "sugarbay",
       'factory': f210}
yocto_builders.append(b210)

#####################################################################
#
# FRI2-noemgd Buildout
#
#####################################################################
f220 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'fri2-noemgd'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'fri2'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f220.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f220)
runPreamble(f220, defaultenv['ABTARGET'])
runBSPLayerPreamble(f220, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f220, "poky", defaultenv['ABTARGET'], "intel")
f220.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f220, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f220)
f220.addStep(NoOp(name="nightly-meta-intel"))
b220 = {'name': "fri2-noemgd",
       'slavenames': ["builder1", "builder1"],
       'builddir': "fri2-noemgd",
       'factory': f220}
yocto_builders.append(b220)

#####################################################################
#
# FRI2 buildout
#
#####################################################################
f225 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'fri2'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'fri2'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f225.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f225)
runPreamble(f225, defaultenv['ABTARGET'])
runBSPLayerPreamble(f225, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f225, "poky", defaultenv['ABTARGET'], "intel")
f225.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f225, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f225)
f225.addStep(NoOp(name="nightly-meta-intel"))
b225 = {'name': "fri2",
       'slavenames': ["builder1", "builder1"],
       'builddir': "fri2",
       'factory': f225}
yocto_builders.append(b225)

#####################################################################
#
# romley buildout
#
#####################################################################
f230 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'romley'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'romley'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f230.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f230)
runPreamble(f230, defaultenv['ABTARGET'])
runBSPLayerPreamble(f230, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f230, "poky", defaultenv['ABTARGET'], "intel")
f230.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f230, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f230)
f230.addStep(NoOp(name="nightly-meta-intel"))
b230 = {'name': "romley",
       'slavenames': ["builder1", "builder1"],
       'builddir': "romley",
       'factory': f230}
yocto_builders.append(b230)

#####################################################################
#
# romley buildout
#
#####################################################################
f235 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'cedartrail'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'cedartrail'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-intel.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-intel"
defaultenv['BSP_REV'] = "HEAD"
f235.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f235)
runPreamble(f235, defaultenv['ABTARGET'])
runBSPLayerPreamble(f235, defaultenv['ABTARGET'], "intel")
buildBSPLayer(f235, "poky", defaultenv['ABTARGET'], "intel")
f235.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f235, "poky-lsb", defaultenv['ABTARGET'], "intel")
runPostamble(f235)
f235.addStep(NoOp(name="nightly-meta-intel"))
b235 = {'name': "cedartrail",
       'slavenames': ["builder1", "builder1"],
       'builddir': "cedartrail",
       'factory': f235}
yocto_builders.append(b235)


################################################################################
# Yocto Master Fuzzy Target
################################################################################
f2 = factory.BuildFactory()
fuzzsched = Triggerable(name="fuzzy-master",
        builderNames=["b2"])
defaultenv['REVISION'] = "HEAD"
defaultenv['ABTARGET'] = 'fuzzy-master'
makeCheckout(f2)
fuzzyBuild(f2)
f2.addStep(Trigger(schedulerNames=['fuzzymastersched'],
                           updateSourceStamp=False,
                           waitForFinish=False))
b2 = {'name': "fuzzy-master",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "fuzzy-master",
      'factory': f2
     }
#yocto_builders.append(b2)
#yocto_sched.append(triggerable.Triggerable(name="fuzzymastersched", builderNames=["fuzzy-master"]))

################################################################################
# Yocto poky-contrib master-under-test Fuzzy Target
################################################################################
f3 = factory.BuildFactory()
fuzzsched = Triggerable(name="fuzzy-mut",
        builderNames=["b3"])
defaultenv['REVISION'] = "HEAD"
defaultenv['ABTARGET'] = 'fuzzy-mut'
makeCheckout(f3)
fuzzyBuild(f3)
f3.addStep(Trigger(schedulerNames=['fuzzymutsched'],
                           updateSourceStamp=False,
                           waitForFinish=False))
b3 = {'name': "fuzzy-mut",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "fuzzy-mut",
      'factory': f3
     }
#yocto_builders.append(b3)
#yocto_sched.append(triggerable.Triggerable(name="fuzzymutsched", builderNames=["fuzzy-mut"]))

################################################################################
# Selectable Targets, for when a nightly fails one or two images
################################################################################
f4 = factory.BuildFactory()
defaultenv['REVISION'] = "HEAD"
defaultenv['ABTARGET'] = 'meta-target'
makeCheckout(f4)
metaBuild(f4)
b4 = {'name': "meta-target",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "meta-target",
      'factory': f4
     }
#yocto_builders.append(b4)


################################################################################
#
# Poky Toolchain Swabber Builder Example Target
#
# Build the toolchain and sdk and profile it with swabber.
# I've set this inactive, but it exists as an example
################################################################################

f22 = factory.BuildFactory()
makeCheckout(f22)
defaultenv['REVISION'] = "HEAD"
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'core-swabber-test'
f22.addStep(ShellCommand, description=["Setting", "SDKMACHINE=i686"], 
            command="echo 'Setting SDKMACHINE=i686'", timeout=10)
defaultenv['SDKMACHINE'] = 'i686'
f22.addStep(ShellCommand, description=["Setting", "ENABLE_SWABBER"], 
            command="echo 'Setting ENABLE_SWABBER'", timeout=10)
defaultenv['ENABLE_SWABBER'] = 'true'
runPreamble(f22, defaultenv['ABTARGET'])
defaultenv['SDKMACHINE'] = 'i686'
runImage(f22, 'qemux86-64', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "intel", False)
f22.addStep(ShellCommand, description="Setting SDKMACHINE=x86_64", 
            command="echo 'Setting SDKMACHINE=x86_64'", timeout=10)
defaultenv['SDKMACHINE'] = 'x86_64'
runImage(f22, 'qemux86-64', 'meta-toolchain-gmae', defaultenv['DISTRO'], False, "intel", False)
if PUBLISH_BUILDS == "True":
    swabberTimeStamp = strftime("%Y%m%d%H%M%S")
    swabberTarPath = BUILD_PUBLISH_DIR + "/swabber-logs/" + swabberTimeStamp + ".tar.bz2"
    f22.addStep(ShellCommand, description=["Compressing", "Swabber Logs"], 
                command="tar cjf " + swabberTarPath + " build/tmp/log", 
                timeout=10000)
b22 = {'name': "core-swabber-test",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "core-swabber-test",
      'factory': f22
     }

yocto_builders.append(b22)

#yocto_sched.append(Nightly(name="Poky Swabber Test", branch=None,
#                                 hour=05, minute=00,
#                                 builderNames=["core-swabber-test"])) 	




################################################################################
#
# Eclipse Plugin Builder
#
# This builds the eclipse plugin. This is a temporary area until this
# gets merged into the nightly & milestone builds
#
################################################################################

f62 = factory.BuildFactory()

f62.addStep(ShellCommand, description="cleaning up eclipse build dir",
            command="rm -rf *",
            workdir=WithProperties("%s", "workdir"))
f62.addStep(ShellCommand, description="Cloning eclipse-poky git repo",
            command="yocto-eclipse-plugin-clone-repo", timeout=300)
f62.addStep(ShellCommand, description="Checking out Eclipse Master Branch",
            workdir="build/eclipse-plugin",
            command="git checkout ADT_helios",
            timeout=60)
f62.addStep(ShellCommand, description="Building eclipse plugin",
            workdir="build/eclipse-plugin/scripts",
            command="./setup.sh",
            timeout=600)
f62.addStep(ShellCommand, description="Building eclipse plugin",
            workdir="build/eclipse-plugin/scripts",
            command="ECLIPSE_HOME=/srv/home/pokybuild/yocto-autobuilder/yocto-slave/eclipse-plugin-helios/build/eclipse-plugin/scripts/eclipse ./build.sh ADT_helios rc4",
            timeout=600)
if PUBLISH_BUILDS == "True":
    f62.addStep(ShellCommand(
                description=["Making eclipse deploy dir"],
                command=["mkdir", "-p", WithProperties("%s/eclipse-plugin/helios", "DEST")],
                env=copy.copy(defaultenv),
                timeout=14400))
    f62.addStep(ShellCommand, description=["Copying eclipse-plugin dir"],
                command=["sh", "-c", WithProperties("cp *.zip %s/eclipse-plugin/helios", "DEST")],
                workdir="build/eclipse-plugin/scripts",
                env=copy.copy(defaultenv),
                timeout=14400)


b62 = {'name': "eclipse-plugin-helios",
      'slavenames': ["builder1",  "builder1"],
      'builddir': "eclipse-plugin-helios",
      'factory': f62,
      }
#yocto_builders.append(b62)

#####################################################################
#
# p1022ds buildout
#
#####################################################################
f240 = factory.BuildFactory()
defaultenv['DISTRO'] = 'poky'
defaultenv['ABTARGET'] = 'p1022ds'
defaultenv['ENABLE_SWABBER'] = 'false'
defaultenv['REVISION'] = "HEAD"
defaultenv['BTARGET'] = 'p1022ds'
defaultenv['BSP_REPO'] = "git://git.yoctoproject.org/meta-fsl-ppc.git"
defaultenv['BSP_BRANCH'] = "master"
defaultenv['BSP_WORKDIR'] = "build/yocto/meta-fsl-ppc"
defaultenv['BSP_REV'] = "HEAD"
f240.addStep(ShellCommand(doStepIf=getCleanSS,
            description="Prepping for nightly creation by removing SSTATE",
            timeout=62400,
            command=["rm", "-rf", defaultenv['LSB_SSTATE_DIR'], defaultenv['SSTATE_DIR']]))
makeCheckout(f240)
runPreamble(f240, defaultenv['ABTARGET'])
runBSPLayerPreamble(f240, defaultenv['ABTARGET'], "fsl")
buildBSPLayer(f240, "poky", defaultenv['ABTARGET'], "fsl")
f240.addStep(ShellCommand, description="Moving old TMPDIR", workdir="build/build", command="mv tmp non-lsbtmp; mkdir tmp")
buildBSPLayer(f240, "poky-lsb", defaultenv['ABTARGET'], "fsl")
runPostamble(f240)
b240 = {'name': "p1022ds",
       'slavenames': ["builder1", "builder1"],
       'builddir': "p1022ds",
       'factory': f240}
yocto_builders.append(b240)
