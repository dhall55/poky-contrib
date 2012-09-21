from django.db import models
from hob.groups.models import Group
from hob.operators.models import Operator

'''
store project info.
'''
class Project(models.Model):
    name = models.CharField(max_length=100)
    groups = models.ManyToManyField(Group)
    operators = models.ManyToManyField(Operator)
    creator = models.CharField(max_length=100)
    description = models.TextField(null=True)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_project'

'''
store user operation history.
'''
class History(models.Model):
    message = models.TextField()
    operator = models.ForeignKey(Operator)
    project = models.ForeignKey(Project)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_history'

'''
store project's advance settings.
'''
class Settings(models.Model):
    image_types = models.TextField(null=True)
    package_formats = models.CharField(max_length=100)
    image_rootfs_size = models.IntegerField(default=0)
    image_extra_size = models.IntegerField(default=0)
    gplv3_checkbox = models.CharField(max_length=50, null=True)
    build_toolchain_checkbox = models.BooleanField(default=False)
    build_toolchain_value = models.CharField(max_length=50)
    distro = models.CharField(max_length=50)
    parellel_make = models.CharField(max_length=20)
    bb_number_threads = models.CharField(null=True, max_length=50)
    max_threads = models.CharField(null=True, max_length=50)
    download_directory = models.CharField(null=True,max_length=500)
    sstate_directory = models.CharField(null=True,max_length=500)
    sstate_mirror = models.CharField(null=True,max_length=500)
    image_type_list = models.CharField(max_length=300)
    package_format_list = models.CharField(max_length=100)
    distro_list = models.CharField(max_length=100)
    build_toolchain_list = models.CharField(max_length=100)
    machine_list = models.CharField(null=True,max_length=500)
    conf_version = models.CharField(null=True,max_length=100)
    kernel_image_type = models.CharField(null=True,max_length=100)
    image_dir = models.CharField(null=True,max_length=500)
    tmp_dir = models.CharField(null=True,max_length=500)
    bb_version = models.CharField(null=True,max_length=100)
    distro_version = models.CharField(null=True,max_length=100)
    lconf_version = models.CharField(null=True,max_length=100)
    core_base = models.CharField(null=True,max_length=300)
    target_os = models.CharField(null=True,max_length=100)
    image_overhead_factor = models.CharField(null=True,max_length=100)
    deployable_image_types = models.CharField(null=True,max_length=300)
    default_task = models.CharField(null=True,max_length=100)
    tune_pkgarch = models.CharField(null=True,max_length=150)
    target_arch = models.CharField(null=True,max_length=150)
    http_proxy = models.CharField(null=True,max_length=300)
    https_proxy = models.CharField(null=True,max_length=300)
    ftp_proxy = models.CharField(null=True,max_length=300)
    note = models.CharField(null=True,max_length=200)
    project = models.ForeignKey(Project)
    creator = models.CharField(max_length=100)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_settings'

'''
store user's advance settings.
'''
class UserSettings(models.Model):
    settings = models.ForeignKey(Settings)
    guid = models.CharField(null=True,max_length=100)
    machine_selected = models.CharField(null=True,max_length=100)
    baseImage_selected = models.CharField(null=True,max_length=100)
    recipes_selected = models.TextField(null=True)
    packages_selected = models.TextField(null=True)
    layers_selected = models.TextField(null=True)
    is_customize_baseImage = models.BooleanField(default=False)
    fast_build_image = models.CharField(null=True,max_length=20)
    build_start = models.CharField(null=True,max_length=100)
    build_conf = models.TextField(null=True)
    build_error = models.TextField(null=True)
    operator = models.ForeignKey(Operator)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_user_settings'

'''
store group of user authority information.
'''
class Permissions(models.Model):
    project = models.ForeignKey(Project, null=True)
    group = models.ForeignKey(Group)
    operators = models.ForeignKey(Operator, null=True)
    ischecked_add_project = models.BooleanField(default=False)
    ischecked_access_del_builds = models.BooleanField(default=False)
    ischecked_add_layer = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_permissions'

'''
store project's layers.
'''
class Layers(models.Model):
    name = models.CharField(max_length=100)
    types = models.CharField(max_length=50)
    project = models.ForeignKey(Project)
    url = models.CharField(max_length=500)
    ischecked = models.BooleanField(default=True)
    creator = models.CharField(max_length=100)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_layers'

'''
store reminder message
'''
class RemindMessage(models.Model):
    content = models.TextField()
    creator = models.CharField(max_length=100)
    receiver = models.CharField(max_length=300)
    types = models.CharField(max_length=100)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_remind_message'
