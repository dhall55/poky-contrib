import time
from xmlrpclib import ServerProxy
from utils import *
import simplejson

from pprint import pprint

#-----test data----------------------
configs = {  'bbthread': 6,
             'distro': 'poky',
             'machine': 'qemux86',
             'package_format': 'rpm',
             'sdk_machine': 'x86_64',
             'sstatedir': '/home/xiaotong/workspace/build_webhob/sstate-cache',
             'sstatemirror': '',
             'dldir': '/home/xiaotong/workspace/build_webhob/downloads',
             'extra_setting': {},
             'image_extra_size': 0,
             'image_fstypes': ' ext3 tar.bz2',
             'image_rootfs_size': 65536,
             'incompat_license': '',
             'layers': ['/home/xiaotong/workspace/python/poky-contrib/meta',
                        '/home/xiaotong/workspace/python/poky-contrib/meta-hob',
                        '/home/xiaotong/workspace/python/poky-contrib/meta-yocto'
                        ],
             'pmake': 6,

             # build package
             'selected_recipes' : ['task-core-boot', 'busybox', 'eglibc-initial', 'libtool-cross', 'libusb1', 'popt', 'udev', 'usbutils', 'sysvinit', 'eglibc', 'udev-extraconf', 'libgcc', 'base-files', 'gdbm', 'perl', 'ncurses', 'kmod', 'modutils-initscripts', 'zip', 'opkg-config-base', 'elfutils', 'pkgconfig', 'gettext', 'binutils-cross', 'gcc-cross-initial', 'v86d', 'netbase', 'libffi', 'sqlite3', 'gcc-cross-intermediate', 'update-modules', 'expat', 'libusb-compat', 'python', 'opkg', 'db', 'bzip2', 'ocf-linux', 'glib-2.0', 'libtool', 'gcc-cross', 'gcc-runtime', 'readline', 'sysvinit-inittab', 'bash', 'tinylogin', 'run-postinsts', 'attr', 'zlib', 'update-rc.d', 'openssl', 'acl', 'initscripts', 'linux-libc-headers', 'linux-yocto', 'pciutils', 'base-passwd'],
 
             # build image
             'is_base_image':1, # 1 or 0
             'selected_image':'core-image-minimal',
             'toolchain_build':[],
             'selected_packages':[],#[] or ['xxx', 'xxxx', 'xx']

             # fast build image
             'is_fast_mode':1,
#             'selected_image':'core-image-minimal',

            # cancel build
             'is_force_cancel':1,
}

config2 =  {'package_format': 'rpm', 'layers': ['/home/an/lxt/poky-contrib/meta', '/home/an/lxt/poky-contrib/meta-yocto', '/home/an/lxt/poky-contrib/meta-hob', '/home/an//meta-skeleton'], 'sstatedir': '/home/an/lxt/build/sstate-cache', 'sstatemirror': '', 'bbthread': '8', 'extra_setting': {}, 'image_extra_size': 0, 'image_rootfs_size': 65536, 'incompat_license': '', 'machine': 'qemux86', 'sdk_machine': 'x86_64', 'dldir': '/home/an/lxt/build/downloads', 'pmake': '8', 'distro': 'poky'}

#configs = simplejson.dumps(configs)
#---------------------------

guid_1 = '11223344' #generate_guid()
guid_2 = generate_guid()


server = ServerProxy('http://localhost:8001', allow_none=True)
#print server.manage_bitbake_server(user1, {'operation': 'add_one_bitbake', 'params': {'ip': '127.0.0.1', 'port': 8889}})
print server.manage_bitbake_server({'operation': 'reset_all'})
try:
    print server.reserve_bitbake_server(guid_1)
except Exception, ex:
    print '1',  ex
#import pprint
#pprint.pprint(server.get_image(guid_1, 'core-image-minimal', 'qemux86', 'ext3 tar.bz2'))

#server.reserve_bitbake_server(guid_2)
#print server.initialize_new_build(guid_1)
print server.parse_configuration(guid_1, config2)

#print server.parse_recipe(guid_1, configs)

#print server.build_package(guid_1, configs)

#print server.build_image(guid_1, configs)
#print server.fast_build_image(guid_1, configs)

#pprint(server.get_image(guid_1, 'core-image-minimal', 'qemux86', 'ext3 tar.bz2'))

#print server.cancel_build(guid_1, 'true')
while True:
    ret_env1 = server.get_ret_event(guid_1)
    pprint(ret_env1)
    print ret_env1
    if isinstance(ret_env1, dict):
        value = ret_env1
        if value.get('done', None):
            break
 
    time.sleep(1)
