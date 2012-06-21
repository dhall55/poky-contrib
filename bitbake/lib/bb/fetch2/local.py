# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
BitBake 'Fetch' implementations

Classes for obtaining upstream sources for the
BitBake build tools.

"""

# Copyright (C) 2003, 2004  Chris Larson
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
# Based on functions from the base bb module, Copyright 2003 Holger Schurig

import os
import urllib
import bb
import bb.utils
from   bb import data
from   bb.fetch2 import FetchMethod, FetchError
from   bb.fetch2 import logger

class Local(FetchMethod):
    def supports(self, url, urldata, d):
        """
        Check to see if a given url represents a local fetch.
        """
        return urldata.type in ['file']

    def urldata_init(self, ud, d):
        # We don't set localfile as for this fetcher the file is already local!
        ud.decodedurl = urllib.unquote(ud.url.split("://")[1].split(";")[0])
        return

    def localpath(self, url, urldata, d):
        """
        Return the local filename of a given url assuming a successful fetch.
        """
        path = urldata.decodedurl
        newpath = path
        if path[0] != "/":
            filespath = data.getVar('FILESPATH', d, True)
            if filespath:
                logger.debug(2, "Searching for %s in paths:    \n%s" % (path, "\n    ".join(filespath.split(":"))))
                newpath = bb.utils.which(filespath, path)
            if not newpath:
                filesdir = data.getVar('FILESDIR', d, True)
                if filesdir:
                    logger.debug(2, "Searching for %s in path: %s" % (path, filesdir))
                    newpath = os.path.join(filesdir, path)
            if not os.path.exists(newpath) and path.find("*") == -1:
                dldirfile = os.path.join(d.getVar("DL_DIR", True), path)
                logger.debug(2, "Defaulting to %s for %s" % (dldirfile, path))
                bb.utils.mkdirhier(os.path.dirname(dldirfile))
                return dldirfile
        return newpath

    def need_update(self, url, ud, d):
        if url.find("*") != -1:
            return False
        if os.path.exists(ud.localpath):
            return False
        return True

    def download(self, url, urldata, d):
        """Fetch urls (no-op for Local method)"""
        # no need to fetch local files, we'll deal with them in place.
        if self.supports_checksum(urldata) and not os.path.exists(urldata.localpath):
            locations = []
            filespath = data.getVar('FILESPATH', d, True)
            if filespath:
                locations = filespath.split(":")
            filesdir = data.getVar('FILESDIR', d, True)
            if filesdir:
                locations.append(filesdir)
            locations.append(d.getVar("DL_DIR", True))

            msg = "Unable to find file " + url + " anywhere. The paths that were searched were:\n    " + "\n    ".join(locations)
            raise FetchError(msg)

        return True

    def checkstatus(self, url, urldata, d):
        """
        Check the status of the url
        """
        if urldata.localpath.find("*") != -1:
            logger.info("URL %s looks like a glob and was therefore not checked.", url)
            return True
        if os.path.exists(urldata.localpath):
            return True
        return False

    def clean(self, urldata, d):
        return

