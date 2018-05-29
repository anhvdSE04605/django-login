from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin import widgets
from .models import *


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, required=True, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(widget=widgets.AdminTimeWidget())

    class Meta:
        model = Profile
        fields = ('birth_date',)
