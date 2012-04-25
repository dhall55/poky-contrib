#!/usr/bin/env python

import sys
import os
import simplejson
import xmlrpclib
try:
    import web
except:
    import traceback
    traceback.print_exc()
    sys.exit('pls install webpy framwork firstly')

rpc_client = xmlrpclib.ServerProxy("http://localhost:9999/")

class GetSsyncValue:
    server = None
    '''
    Get synchronous values:
    ---------------------------------------------------------------------------
      BBLAYERS,DL_DIR,MACHINE,DISTRO,PACKAGE_CLASSES,SSTATE_DIR,SSTATE_MIRROR
      BB_NUMBER_THREADS,getCpuCount,PARALLEL_MAKE,DEPLOY_DIR_IMAGE
      IMAGE_ROOTFS_EXTRA_SPACE,INCOMPATIBLE_LICENSE,SDKMACHINE,SDK_ARCH, etc.
    ---------------------------------------------------------------------------
    '''
    def GET(self, param=''):
        param = str(param).strip()
        retValue = None
        if param:
            try:
                if param == 'getCpuCount':
                    retValue = {param: rpc_client.get_cpu_count()}
                else:
                    retValue = {param: rpc_client.get_config_item(param)}
            except Exception as e:
                retValue = {'req_param':param, 'error_info':str(e)}
        return simplejson.dumps(retValue)

class SendAction:
    '''
    Send these commands , parsing recipe, building package, building image, etc.
    '''
    def GET(self, param=''):
        param = str(param).strip()
        retValue = None
        try:
            if param == 'initcooker':
                rpc_client.init_cooker()
                retValue = {'action':param, "status":'OK'}
            elif param == 'resetcooker':
                rpc_client.reset_cooker()
                retValue = {'action':param, "status":'OK'}
            elif param == 'forcecancelbuild':
                rpc_client.cancel_build(True)
                retValue = {'action':param, "status":'OK'}
            elif param == 'unforcecancelbuild':
                rpc_client.cancel_build(False)
                retValue = {'action':param, "status":'OK'}
            elif param == 'asyncconfs':
                rpc_client.generate_async_configs()
                retValue = {'action':param, "status":'OK'}
            elif param == 'getevents':
                event = rpc_client.popEvent()
                queue = []
                while event:
                    queue.append(event)
                    event = rpc_client.popEvent()

                retValue = {'queue':queue}
            else:
                if param in ('parserecipe','buildpkg', 'buildimage'):
                     retValue = "ERROR: Current URL '/action/%s' only supports http post request" % param
                else:
                    retValue = 'ERROR: (Page 404, url not Found)'
                return retValue
        except Exception as e:
                retValue = {'req_param':param, 'error_info':str(e)}

        return simplejson.dumps(retValue)

    def POST(self, param=''):
        param = str(param).strip()
        retValue = None
        # the following handling form codes is temporary.
        # http form valitation is necessary. so should improve here later.
        try:
            layers = web.input().layers.strip()
            if len(layers)>0 and layers.startswith('['):
                layers = eval(layers)

            sstatedir = web.input().sstatedir.strip()
            sstatemirror = web.input().sstatemirror.strip()

            bbthread = web.input().bbthread.strip()
            pmake = web.input().pmake.strip()
            bbthread = int(bbthread)
            pmake = int(pmake)

            extra_setting = {}
            image_extra_size = web.input().image_extra_size.strip() or '0'
            image_extra_size = int(image_extra_size)
            curr_package_format = web.input().curr_package_format.strip()
            if len(curr_package_format)>0 and curr_package_format.startswith('['):
                curr_package_format = eval(curr_package_format)
                curr_package_format = ' '.join(curr_package_format)

            incompat_license = web.input().incompat_license.strip()  or ''
            curr_mach = web.input().curr_mach.strip()
            curr_sdk_machine = web.input().curr_sdk_machine.strip()
            packageinfo = 'packageinfo'
            dldir = web.input().dldir.strip()
            curr_distro = web.input().curr_distro.strip()
        except AttributeError as e:
            return simplejson.dumps({'error':'Form parameter %s is required' % str(e)})

        configs = {'layers': layers,
                  'sstatedir': sstatedir,
                  'sstatemirror': sstatemirror,
                  'bbthread': bbthread,
                  'extra_setting': extra_setting,
                  'image_extra_size': image_extra_size,
                  'curr_package_format': curr_package_format,
                  'incompat_license': incompat_license,
                  'curr_mach': curr_mach,
                  'curr_sdk_machine': curr_sdk_machine,
                  'packageinfo': packageinfo,
                  'dldir': dldir,
                  'pmake': pmake,
                  'curr_distro': curr_distro}

        if param == 'parserecipe':
            rpc_client.set_user_config(configs)
            rpc_client.generate_recipes()
            retValue = {'action':param, "status":'OK'}
        elif param == 'buildpkg':
            rcp_list = web.input().rcp_list.strip()
            if len(rcp_list)>0 and rcp_list.startswith('['):
                rcp_list = eval(rcp_list)
            else:
                return simplejson.dumps({'action':param,
                                         "status":'ERROR',
                                         "error_info": '(current rcp_list = %s)rcp_list value is wrong' % rcp_list})

            rpc_client.set_user_config(configs)
            rpc_client.generate_packages(rcp_list)
            retValue = {'action':param, "status":'OK'}
        elif param == 'buildimage':
            pkg_list = web.input().pkg_list.strip()
            rcp_list = web.input().rcp_list.strip()
            fast_mode = web.input().fast_mode.strip()
            if len(rcp_list)>0 and rcp_list.startswith('['):
                rcp_list = eval(rcp_list)
            else:
                return simplejson.dumps({'action':param,
                                         "status":'ERROR',
                                         "error_info": '(current rcp_list = %s)rcp_list value is wrong' % rcp_list})

            if len(pkg_list)>0 and pkg_list.startswith('['):
                pkg_list = eval(pkg_list)
            else:
                return simplejson.dumps({'action':param,
                                         "status":'ERROR',
                                         "error_info": '(current pkg_list = %s)pkg_list value is wrong' % pkg_list})
            if fast_mode:
                fast_mode = eval(fast_mode)
            else:
                fast_mode = False
            rpc_client.set_user_config(configs)
            rpc_client.generate_image(rcp_list, pkg_list, fast_mode)
            retValue = {'action':param, "status":'OK'}

        return simplejson.dumps(retValue)

urls = (
    '/get/(\w+)', 'GetSsyncValue',
    '/action/(\w+)', 'SendAction',
    )

web.config.debug = False
app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
