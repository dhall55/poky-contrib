import os
import ftplib
import time

_all_upload_dirs = {}

class UploadLayers(object):
    layer_pkg_types = ["tar.bz2", "tar.gz", "zip"]
    MAX_FILE_SIZE = (500 * 2**20) # 500 MB

    def __init__(self, interface=("localhost", 21), uid="ftp", password="", layer_root_dir="share_layers"):
        self.host = interface[0]
        self.port = interface[1]
        self.login = uid
        self.passwd = password
        self.upload_bb_layers_root = layer_root_dir
        self.total_size = 0
        self.publish_files = {}

    def regist_upload_layer(self, prj_name, layer_dir, upload_layer_name):
        """  regist new layer as some steps of layer checking, if passed it will be save to db or mem recorder """
        if not _all_upload_dirs.has_key(prj_name):
            _all_upload_dirs[prj_name] = {}
            _all_upload_dirs[prj_name]['uplayers_dir'] = layer_dir
            _all_upload_dirs[prj_name]['uplayers'] = []
        _all_upload_dirs[prj_name]['uplayers'].append(upload_layer_name)

    def assert_file_serv(self, serv, file_addr):
        """ checking the file srv states to assert it can be shared to bit_bake or not
        """
        resp = "not start"
        if os.path.exists(file_addr):
            try:
                resp = os.system('sudo service portmap status')
            except:
                resp = "not start"
        return resp

    def assert_layer(self, file_obj):
        try:
            self.publish_files = {}

            fullname = file_obj.name
            ext = ""
            for t in self.layer_pkg_types:
                if fullname.endswith(t):
                    ext = t
            if not ext:
                return ("invalid request: unknown layer pkg type : %s" % ext)

            # get the compressed layer file
            file_name = ((fullname.split("/"))[-1])
            tmp_file = open(os.path.join(os.curdir, file_name), 'wb')
            for raw_data in file_obj.chunks():
                self.total_size += len(raw_data)
                if self.total_size < self.MAX_FILE_SIZE:
                    tmp_file.write(raw_data)
                else:
                    tmp_file.close()
                    os.remove(tmp_file.name)
                    return ("invalid request: too large file")

            tmp_file.close()

            layer_name = file_name.split('.')[0]
            # create a temp dir to extract the all files
            localpath = os.path.join(os.curdir, 'tt/')
            if os.path.exists(localpath):
                os.system('rm -rf %s' % localpath)
            os.mkdir(localpath)

            is_extracted = False
            if ext == "tar.bz2" or ext == "tar.gz":
                os.system("tar -xf %s -C %s" % (tmp_file.name, localpath))
                os.remove(tmp_file.name)
                is_extracted = True
            elif ext == "zip":
                os.system("unzip -o -d %s %s" % (localpath, tmp_file.name))
                os.remove(tmp_file.name)
                is_extracted = True
            else:
                pass

            if is_extracted:
                # check has the layer.conf or not
                try:
                    fpipe = os.popen('find %s -name layer.conf ' % os.path.abspath(localpath))
                    if fpipe:
                        chk_layer_conf = fpipe.readline().lstrip('\n').rstrip('\n')
                        fpipe.close()
                    else:
                        return "invalid request: layer checking fault"

                except OSError as exc:
                    return ("invalid request:Io except:%s" % exc)

                if os.path.exists(chk_layer_conf) and os.path.isfile(chk_layer_conf):
                    names = [os.path.abspath(os.path.join(localpath, name)) for name in os.listdir(localpath)]
                    names.sort()
                    self.publish_files[(layer_name, localpath)] = names
                else:
                    os.system('rm -rf %s' % localpath)
                    return ("unknown layer pkg : %s by no layer.conf" % layer_name)

        except Exception, e:
            from traceback import format_exc
            return format_exc()

        return 'pass layer checking'

    def switch_into_dir(self, ftp, base_dir):
        try:
            ftp.cwd(base_dir)
        except ftplib.error_perm:
            ftp.mkd(base_dir)
            time.sleep(0.05)
            ftp.cwd(base_dir)

    def send_folder(self, serv, source_dir, root_dir, base_dir):
        dirname = source_dir.replace(base_dir, root_dir)
        self.switch_into_dir(serv, dirname)
        # get path of listed files
        is_dir_changed = False
        names = [os.path.abspath(os.path.join(source_dir, name)) for name in os.listdir(source_dir)]
        for s in names:
            if os.path.isdir(s):
                self.send_folder(serv, s, root_dir, base_dir)
                is_dir_changed = True
            elif os.path.isfile(s):
                if is_dir_changed:
                    is_dir_changed = False
                    serv.cwd(dirname)

                f = open(s,'rb')
                name = (f.name.split('/'))[-1]
                serv.storbinary('STOR '+ name, f)
                f.close()

    def get_root_relstart(self, path, start):
        related_start = start
        if path.endswith('/'):
            if not start.endswith('/'):
                related_start = related_start + '/'
        if not start.startswith('/'):
            related_start = '/' + related_start

        return related_start

    def transmit(self, prj_name, file_obj):
        ret = self.assert_layer(file_obj)
        if not self.publish_files:
            return ret

        key = (layer, tmp_dir) = (self.publish_files.keys())[0]
        # connect to ftp and login
        ftp = None
        try:
            if self.host == 'localhost':
                ftp = ftplib.FTP('localhost')
            else:
                ftp = ftplib.FTP()
		ftp.connect(self.host, self.port)
            ftp.login(self.login, self.passwd)
        except Exception, e:
            return "load file server error, (%s, %s)" % (self.host, self.port)
        # create the base dir upload_ftp_root/prjname/layer
        self.switch_into_dir(ftp, "upload")
        b_dir = str("%s" % prj_name.split('/')[-1])
        self.switch_into_dir(ftp, b_dir)
        layer = str("%s" % layer)
        self.switch_into_dir(ftp, layer)
        b_dir += '/' + layer

        filepath = self.publish_files[key][0]
        filename = 'transmit.log'
        try:
            if os.path.isdir(filepath):
                root_start = self.get_root_relstart(filepath, "upload/" + b_dir)
                self.send_folder(ftp, filepath, root_start, filepath)
            else: # file to send
                f = open(filepath, 'rb')
                ftp.storbinary('STOR '+ filename, f)
                f.close()
        except Exception:
            from traceback import format_exc
            return format_exc()

        layerpath = self.upload_bb_layers_root + '/' + b_dir
        self.regist_upload_layer(prj_name, layerpath, layer)

        # cancel the temp dir and publish files
        self.publish_files = None
        os.system('rm -rf %s' % tmp_dir)

        return "transmition completed", layerpath