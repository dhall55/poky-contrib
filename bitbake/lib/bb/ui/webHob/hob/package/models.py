from django.db import models
from hob.utils.utils import _size_to_string, _string_to_size

class PackageManager(models.Manager):
    def populate(self, pkginfolist, guid):
        for pkginfo in pkginfolist:
            pn = pkginfo['PN']
            pv = pkginfo['PV']
            pr = pkginfo['PR']
            pnpvpr = pn+'-'+pv+'-'+pr
            pkg = pkginfo['PKG']
            pkgv = pkginfo['PKGV']
            pkgr = pkginfo['PKGR']
            pkgsize = pkginfo['PKGSIZE_%s' % pkg] if 'PKGSIZE_%s' % pkg in pkginfo.keys() else "0"
            pkg_rename = pkginfo['PKG_%s' % pkg] if 'PKG_%s' % pkg in pkginfo.keys() else ""
            section = pkginfo['SECTION_%s' % pkg] if 'SECTION_%s' % pkg in pkginfo.keys() else ""
            summary = pkginfo['SUMMARY_%s' % pkg] if 'SUMMARY_%s' % pkg in pkginfo.keys() else ""
            rdep = pkginfo['RDEPENDS_%s' % pkg] if 'RDEPENDS_%s' % pkg in pkginfo.keys() else ""
            rrec = pkginfo['RRECOMMENDS_%s' % pkg] if 'RRECOMMENDS_%s' % pkg in pkginfo.keys() else ""
            rprov = pkginfo['RPROVIDES_%s' % pkg] if 'RPROVIDES_%s' % pkg in pkginfo.keys() else ""

            if 'ALLOW_EMPTY_%s' % pkg in pkginfo.keys():
                allow_empty = pkginfo['ALLOW_EMPTY_%s' % pkg]
            elif 'ALLOW_EMPTY' in pkginfo.keys():
                allow_empty = pkginfo['ALLOW_EMPTY']
            else:
                allow_empty = ""

            if pkgsize == "0" and not allow_empty:
                continue

            # pkgsize is in KB
            size = _size_to_string(_string_to_size(pkgsize + ' KB'))
            rdeprec = rdep+' '+ rrec
            rdeprec = rdeprec.strip()
            self.create(guid = guid,
                        name       = pkg,
                        pnpvpr     = pnpvpr,
                        pkgv       = pkgv,
                        pkgr       = pkgr,
                        pkg_rename = pkg_rename,
                        summary    = summary,
                        section    = section,
                        rdep       = rdeprec,
                        rprov      = rprov,
                        size       = size,
                        binb       = '',
                        is_inc     = 0,
            )

class PackageModel(models.Model):
    guid = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    pnpvpr = models.CharField(max_length=1000)
    pkgv = models.CharField(max_length=1000)
    pkgr = models.CharField(max_length=1000)
    pkg_rename = models.CharField(max_length=1000)
    summary = models.CharField(max_length=4000)
    section = models.CharField(max_length=1000)
    rdep = models.TextField()
    rprov = models.CharField(max_length=1000)
    size = models.CharField(max_length=200)
    binb = models.CharField(max_length=5000)
    is_inc = models.IntegerField()
    objects = PackageManager()
    class Meta:
        db_table = u'db_package_model'
        ordering = ['name']