from django.db import models
from hob.operators.models import Operator
from hob.projects.models import Project

'''
store image url
'''
class Images(models.Model):
    name = models.CharField(max_length=300)
    size = models.DecimalField(decimal_places=2, max_digits=5, default =0.0)
    url = models.TextField()
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_images'

'''
store build records
'''
class Builds(models.Model):
    guid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    size = models.DecimalField(decimal_places=2, max_digits=5, default =0.0)
    images = models.ManyToManyField(Images)
    project = models.ForeignKey(Project)
    operator = models.ForeignKey(Operator)
    valid = models.BooleanField(default=True)
    is_share = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_builds'

'''
store build process
'''
class Building(models.Model):
    guid = models.CharField(max_length=100)
    name = models.CharField(max_length=300)
    current_build_task = models.CharField(max_length=100)
    build_percent = models.DecimalField(decimal_places=2, max_digits=5, default =0.0)
    estimated_size = models.DecimalField(decimal_places=2, max_digits=5, default =0.0)
    estimated_time = models.DecimalField(decimal_places=2, max_digits=5, default =0.0)
    is_finished = models.BooleanField(default=False)
    project = models.ForeignKey(Project)
    operator = models.ForeignKey(Operator)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_building'