'''
Created on 2012-5-14
@author: lvchunhx
'''
from django import forms
from management.models import Bitbakeserver, Operator
class BitbakeForm(forms.ModelForm):
    class Meta:
        model = Bitbakeserver

class userForm(forms.ModelForm):
    email = forms.CharField(max_length=600, required=False)
    valid = forms.CharField(max_length=3, required=False)
    class Meta:
        model = Operator
        exclude = ('bitbakeserver',)