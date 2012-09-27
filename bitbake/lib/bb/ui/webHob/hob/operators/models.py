from django.db import models

'''
store user's role info.
'''
class SystemConfig(models.Model):
    types = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_systemConfig'

'''
store user's info.
'''
class Operator(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.ForeignKey(SystemConfig)
    is_login = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    class Meta:
        db_table = u'db_operator'