'''
Created on 2012-5-14
@author: lvchunhx
'''
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=300)
    password = forms.CharField(max_length=300)

class advanceSettingForm(forms.Form):
    image_rootfs = forms.CharField(required=False)
    image_extra = forms.CharField(required=False)
    exclude_gplv3 = forms.CharField(required=False)
    build_toolchain = forms.CharField()
    distro = forms.CharField()
    bb_number_threads = forms.CharField()
    parallel_make = forms.CharField(required=False)
    download_directory = forms.CharField()
    sstate_directory = forms.CharField(required=False)
    sstate_mirror = forms.CharField(required=False)