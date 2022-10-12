from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='email')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    # Checking that an email doesn't exist
    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return self.cleaned_data

    # Committing the cleaned data
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
