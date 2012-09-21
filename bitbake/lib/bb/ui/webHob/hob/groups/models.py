from django.db import models
from hob.operators.models import Operator

class Group(models.Model):
    name = models.CharField(max_length=100)
    valid = models.BooleanField(default=True)
    creator = models.CharField(max_length=100)
    create_date = models.DateTimeField(auto_now=True,blank=True)
    operators = models.ManyToManyField(Operator)
    class Meta:
        db_table = u'db_group'