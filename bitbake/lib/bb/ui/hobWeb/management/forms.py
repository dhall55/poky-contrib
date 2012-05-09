#coding=utf-8
'''
Created on 2012-4-15

@author: lvchunhx
'''
from django.forms import ModelForm
from models import Bitbakeserver,Operator

class LoginForm(ModelForm):
    class Meta:
        model = Operator
        exclude = ('bitbakeserver',)

class BitbakeServerForm(ModelForm):
    class Meta:
        model = Bitbakeserver
