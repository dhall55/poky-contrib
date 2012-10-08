#!/usr/bin/env python
# OpenEmbedded Release Utility
#
# Written by: Elizabeth Flanagan <elizabeth.flanagan@intel.com>
#
# Copyright 2012 Intel Corporation
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
#
#


import os, sys, optparse, subprocess, fnmatch, shutil
#print os.path.join(
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '../bitbake/lib'))
import bb.tinfoil

usage  = """%prog [options] gplonly|all

Gather up required sources after a bitbake run, do some minor modifications 
to it and package it with your current checkout out copy of your build system 
into a single releaseable tarball. This should only be run post-image creation.
"""

parser = optparse.OptionParser(usage=usage)
options, args = parser.parse_args( sys.argv )

if len(args) != 2 or (sys.argv[1] != "gplonly" and sys.argv[1] != "all") :
    parser.error("""
    You must specify if you wish to package *GPL* sources only or all sources. 
    """ + usage )
releasetype=sys.argv[1]
bbhandler = bb.tinfoil.Tinfoil()
bblayers = (bbhandler.config_data.getVar('BBLAYERS', True) or "").split()
dldir = (bbhandler.config_data.getVar('DL_DIR', True) or "").split()[0]
deploydir = (bbhandler.config_data.getVar('DEPLOY_DIR', True) or "").split()[0]
sourcesdir = os.path.join(deploydir, "sources")
licensedir = (bbhandler.config_data.getVar('LICENSE_DIRECTORY', True) or "").split()[0]
tmpdir = (bbhandler.config_data.getVar('TMPDIR', True) or "").split()[0]
# Much better way to do this, but keeping it simple for now
layers_hash = {}
layers_repo = {}
layers_branch = {}
layers = {}

for layer in bblayers:
    githash=subprocess.check_output("git rev-parse HEAD", shell=True, cwd=layer).strip()
    if githash not in layers_hash.values():
        layers_hash[layer]=githash
        layers_branch[layer]=subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True, cwd=layer).strip()
        layers_repo[layer]=subprocess.check_output("git config --get remote.origin.url", shell=True, cwd=layer).strip()

# From here, pull together build system components

series_matches = []
for root, dirnames, filenames in os.walk(sourcesdir):
    for filename in fnmatch.filter(filenames, '*-series.*'):
        if releasetype=="gplonly":
            if "GPL" in os.path.dirname(root):
                series_matches.append(os.path.join(root, filename))
        else:
            series_matches.append(os.path.join(root, filename))

source_matches = []
for root, dirnames, filenames in os.walk(sourcesdir):
    for filename in filenames:
        if "-series." not in filename:
            if releasetype=="gplonly":
                if "GPL" in os.path.dirname(root):
                    source_matches.append(os.path.join(root, filename))
            else:
                source_matches.append(os.path.join(root, filename))
for line in source_matches:
    print line

staging_workdir = os.path.join(os.path.join(tmpdir, "release"))
try:
    os.removedirs(staging_workdir)
except:
    pass
try:
    os.makedirs(staging_workdir)
except:
    pass


for source in source_matches:
    source_basename = os.path.basename(source)
    source_workdir = os.path.join(os.path.join(tmpdir, os.path.join("work_release", source_basename + "_work")))
    if "prepatch" in source:
        # this is a git repo. Cat .git/config and grab from DL_DIR
        git_repo_name = ""
#        print "Moving " + source + " to " + source_workdir
        try:
            os.remove(os.path.join(source_workdir))
        except:
            pass
        try:
            os.makedirs(source_workdir)
        except:
            pass
        shutil.copyfile(source, os.path.join(source_workdir, source_basename))
        subprocess.call(["tar", "xzf", os.path.join(source_workdir, source_basename)], cwd=source_workdir)
        if os.path.exists(source_workdir + "/git/.git/config"):
            f = open(source_workdir + "/git/.git/config")
            for line in f:
                if "url =" in line:
                    git_repo_name = line.replace('url = ', '').replace(dldir,'').replace("/", "_").strip()
            git_repo_name = git_repo_name[:-1] if git_repo_name.endswith('_') else git_repo_name
            git_repo_name = git_repo_name[1:] if git_repo_name.startswith('_') else git_repo_name
            print "Extracted " + source_basename + " to " + source_workdir +". The repo is " + git_repo_name
            subprocess.call(["tar", "czvf", "../" + git_repo_name + ".tar.gz", "."], cwd=source_workdir+"/git")
            shutil.copyfile(os.path.join(source_workdir, git_repo_name + ".tar.gz"), os.path.join(staging_workdir, git_repo_name + ".tar.gz"))
        elif "svn" not in source:
            source_name = subprocess.check_output("tar -ztf" + source, shell=True).strip().split('/')[1]
        elif "svn" in source:
            # Ugh, I dislike how svn repos got packed.
            svn_rev=source_basename.split("+")[1].split("-")[0].replace("r", "_")
            dl_name=source_basename.split("-")[0]
            for files in os.listdir(dldir):
                if dl_name in files and svn_rev in files:
                    shutil.copyfile(os.path.join(dldir, files), os.path.join(staging_workdir, files))

for series in series_matches:
    print "Extracting " + series + " to staging DL_DIR."
    series_basename = os.path.basename(series)
    shutil.copyfile(series, os.path.join(staging_workdir, series_basename))
    subprocess.call(["tar", "xzf", os.path.join(staging_workdir, series_basename)], cwd=staging_workdir)
    os.remove(os.path.join(staging_workdir, series_basename))
    series_untar_dir = os.path.join(staging_workdir, series_basename.replace(".tar.gz", ""))
    for files in os.listdir(series_untar_dir):
        shutil.move(os.path.join(series_untar_dir, files), os.path.join(staging_workdir, files))
    os.removedirs(os.path.join(staging_workdir, series_untar_dir))

