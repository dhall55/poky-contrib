from django.db import models

class Bitbakeserver(models.Model):
    name = models.CharField(max_length=150, blank=True)
    ip = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=300, blank=True, default='0')
    port = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'bitbakeserver'

class Operator(models.Model):
    username = models.CharField(max_length=300)
    password = models.CharField(max_length=300)
    email = models.CharField(max_length=600, default='xxx@intel.com')
    valid = models.CharField(max_length=3, default='1')
    status = models.CharField(max_length=150, blank=True, default='0')
    create_date = models.DateTimeField(auto_now=True, blank=True)
    bitbakeserver = models.ForeignKey(Bitbakeserver, null=True)
    class Meta:
        db_table = u'operator'