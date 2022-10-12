from django import forms
from .models import Member, CSV
from django.forms import EmailField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class MemberForm(forms.ModelForm):
    # defining the model to being the Meta
    class Meta:
        model = Member
        # all our field names within the Member model
        fields = ['email', 'firstName', 'lastName', 'phoneNumber', 'jobDesc', 'yearsExperience','User']


class CSVForm(forms.ModelForm):
    class Meta:
        model = CSV
        fields = ('file_name',)
