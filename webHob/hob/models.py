from django.db import models
from management.models import Operator, Bitbakeserver

class BuildConfig(models.Model):
    operator = models.ForeignKey(Operator,null=True)
    bitbakeserver = models.ForeignKey(Bitbakeserver,null=True)
    image_type = models.CharField(null=True,max_length=150, blank=True)
    package_format = models.CharField(null=True,max_length=150, blank=True)
    image_rootfs = models.IntegerField(null=True,default=0)
    image_extra = models.IntegerField(null=True,default=0)
    exclude_gplv3 = models.BooleanField(default=False)
    build_toolchain = models.CharField(null=True,max_length=300, blank=True)
    distro = models.CharField(null=True,max_length=300, blank=True)
    bb_number_threads = models.IntegerField(null=True,blank=True,default='8')
    parallel_make = models.IntegerField(null=True,blank=True,default='8')
    download_directory = models.CharField(null=True,max_length=500, blank=True)
    sstate_directory = models.CharField(null=True,max_length=500,blank=True)
    sstate_mirror = models.CharField(null=True,max_length=500,blank=True)
    key_value_variable = models.CharField(null=True,max_length=500,blank=True)
    layers = models.CharField(null=True,max_length=500,blank=True)
    machine = models.CharField(null=True,max_length=200,blank=True)
    base_image = models.CharField(null=True,max_length=150,blank=True)
    recipes = models.TextField(null=True)
    recipe_total = models.IntegerField(null=True,default=0)
    tasks = models.TextField(null=True)
    task_total = models.IntegerField(null=True,default=0)
    packages = models.TextField(null=True)
    package_total = models.IntegerField(null=True,default=0)
    package_size = models.IntegerField(null=True,default=0)
    image_url = models.CharField(null=True,max_length=300,blank=True)
    image_size = models.IntegerField(default=0)
    build_result = models.BooleanField(default=False)
    create_date = models.DateTimeField(null=True,auto_now=True, blank=True)
    class Meta:
        db_table = u'buildConfig'

class TreeModel(models.Model):
    types = models.CharField(null=True,max_length=50,blank=True)
    name = models.CharField(null=True,max_length=500,blank=True)
    license = models.CharField(null=True,max_length=500,blank=True)
    group = models.CharField(null=True,max_length=500,blank=True)
    description = models.TextField(null=True)
    size = models.IntegerField(null=True,default=0)
    pkg_parent = models.CharField(null=True,max_length=500,blank=True)
    is_included = models.BooleanField(default=False)
    brought_in_by = models.CharField(null=True,max_length=500,blank=True)
    create_date = models.DateTimeField(null=True,auto_now=True,blank=True)
    operator = models.ForeignKey(Operator,null=True)
    class Meta:
        db_table = u'treeModel'

class SystemConfig(models.Model):
    name = models.CharField(max_length=100,blank=True)
    types = models.CharField(max_length=20,blank=True)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'systemConfig'