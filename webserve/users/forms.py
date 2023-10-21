from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email'}), label='Email')
