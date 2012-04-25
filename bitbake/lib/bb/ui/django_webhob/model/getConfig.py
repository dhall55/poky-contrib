import sys
import urllib, urllib2
import simplejson

def req_url(url_prefix='http://localhost:8080/', path='',  method='get', params={}):
    if method == 'get':
        if params:
            param = urllib.urlencode(params)
            url = "%s%s?%s" % (url_prefix, path, param)
        else:
            url = "%s%s" % (url_prefix, path)
        request = urllib2.Request(url)
    elif method == 'post':
        params = urllib.urlencode(params)
        url = "%s%s" % (url_prefix, path)
        request = urllib2.Request(url, params)
    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        sys.exit(str(e))
    return response.read()

def getssync(path='', url_prefix='http://localhost:8080/'):
    v = ''
    res = req_url(url_prefix, "get/"+path)
    if res:
        json = simplejson.loads(res)
        v = json[path]
    return v

def getssyncConfigss():
    params = {}
    image_addr_prefix = ""
    params["layer"] = getssync("BBLAYERS").split()
    params["dldir"] = getssync("DL_DIR")
    params["machine"] = getssync("MACHINE")
    params["distro"] = getssync("DISTRO")
    params["pclass"] = getssync("PACKAGE_CLASSES")
    params["sstatedir"] = getssync("SSTATE_DIR")
    params["sstatemirror"] = getssync("SSTATE_MIRROR")
    num_threads = getssync("getCpuCount")
    if not num_threads:
        num_threads = 1
        max_threads = 65536
    else:
        num_threads = int(num_threads)
        max_threads = 16 * num_threads
    params["max_threads"] = max_threads
    bbthread = getssync("BB_NUMBER_THREADS")
    if not bbthread:
        bbthread = num_threads
    else:
        bbthread = int(bbthread)
    params["bbthread"] = bbthread
    pmake = getssync("PARALLEL_MAKE")
    if not pmake:
        pmake = num_threads
    else:
        pmake = int(pmake.lstrip("-j "))
    params["pmake"] = pmake
    image_addr = getssync("DEPLOY_DIR_IMAGE")
    if image_addr_prefix:
        image_addr = image_addr_prefix + image_addr
    params["image_addr"] = image_addr
    image_extra_size = getssync("IMAGE_ROOTFS_EXTRA_SPACE")
    if not image_extra_size:
        image_extra_size = 0
    else:
        image_extra_size = int(image_extra_size)
    params["image_extra_size"] = image_extra_size
    params["incompat_license"] = getssync("INCOMPATIBLE_LICENSE")
    params["sdk_machine"] = getssync("SDKMACHINE") or getssync("SDK_ARCH")
    return params
#---------------------------------------------------------------------------------