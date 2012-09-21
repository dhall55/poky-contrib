from django import forms
class OperatorForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()