import email
from re import M
from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User


# from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class Member(models.Model):
    phoneNumber = models.CharField(max_length=30, unique=True, primary_key=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=100)
    jobDesc = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    yearsExperience = models.IntegerField()
    User = models.OneToOneField(User, related_name="member", on_delete=models.CASCADE)

    def __str__(self):
        return self.firstName + ' ' + self.lastName


# A model to store the uploaded contacts for processing.
class CSV(models.Model):
    file_name = models.FileField(upload_to='csvs')
    uploaded = models.DateTimeField(auto_now_add=True)
    # This allows us to edit the most recently added file.
    validated = models.BooleanField(default=False)

    def __str__(self):
        return ("File id: {self.id}")


# All contacts imported from all users
class GlobalContactList(models.Model):
    # We need this to be unique however as not all of the member contacts
    # will be using our application, we don't need a relation to an existing phone number.
    phoneNumber = models.CharField(max_length=30, unique=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=100)

    # String representation of an object with this model.
    def __str__(self):
        return f"name:{self.firstName}+{self.lastName}--contact:{self.phoneNumber}"


# This model will hold which Member has which contact.
# Rather than using a foreign key we are using the OneToOneField
# This allows for a reverse accesor, letting us reference a field in the member model while accessing MemberContactList.
# Primary key can be considered conceptually as a composite of phoneNumber & contact fields.
class MemberContactList(models.Model):
    # We want the data in the Member model to be reflected in our Member's contact list.
    Member = models.ForeignKey(Member, related_name="member", on_delete=models.CASCADE)
    # Storing the user's contact
    contact = models.CharField(max_length=30)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # job_desc and years_experience are the fields this pertains to and in the event
    # of deletion we want any changes to propagate through all of our models.

    # String representation of an object with this model.
    def __str__(self):
        return f"name:{self.Member.firstName}+{self.Member.lastName}--contact:{self.contact}"


class OpenRequest(models.Model):
    # This model represents an open request between the sender and the requestee.
    # Mutual needs to approve intial request before it is viewable by requestee. Hence two auth boolean values.
    # Full objects stored for easy refrencing later.
    sender = models.ForeignKey(Member, related_name="sender", on_delete=models.CASCADE)
    mutual = models.ForeignKey(Member, related_name="mutual", on_delete=models.CASCADE)
    requestee = models.ForeignKey(Member, related_name="requestee", on_delete=models.CASCADE)
    auth1 = models.BooleanField()
    auth2 = models.BooleanField()

    def __str__(self):
        return f"sender:{self.sender}+mutual{self.mutual}+requestee{self.requestee}"
