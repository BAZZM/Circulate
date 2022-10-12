from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import Member, CSV, GlobalContactList, MemberContactList, OpenRequest
# importing our forms
from .forms import MemberForm, CSVForm
# importing messages module used to provide custom messages for users when validating.
from django.contrib import messages
# Importing csv module for when we import the user contacts
import csv
from django.db.models import Q


# Create your views. here.

def index(request):
    # If user is logged in and fully registered we can then create a list of their inner circle / contacts.
    if request.user.is_authenticated:
        try:
            # Find the currently logged in user's profile to match with the Member field in MCL model.
            # Allowing us to query all user's contacts.
            userProfile = request.user.member
            inferredContacts = request.user.member.phoneNumber
            #We have to perform a complex query to check both fields for instances of our user.
            contactList = MemberContactList.objects.filter(Q(Member=userProfile) or Q(contact=inferredContacts))
            contacts = []
            contactsRich = []
            # Appending to a new list with the contact's phone number for processing individually.
            for contact in contactList:
                contacts.append(contact.contact)
            print(contacts)
            # Now we have selected all the contacts within our user's list
            # We can gather some richer data for displaying on the page.
            for number in contacts:
                # Selecting the rest of the relevant data to the Member's contacts.
                contactRich = Member.objects.filter(phoneNumber=number).values('firstName', 'lastName', 'phoneNumber',
                                                                               'jobDesc', 'yearsExperience')
                contactsRich.append(contactRich)

        except:
            print("Member does not have a registered profile.")
            return render(request, 'complete.html', context={})
    all_members = Member.objects.all()
    # Fills a list with all registered User emails
    registeredEmails = []
    for item in all_members:
        registeredEmails.append(item.email)
    # Depending on user's authentications status we will have to render the page with different context dictionaries.
    if request.user.is_authenticated:
        return render(request, 'index.html',
                      context={'all': all_members, 'regEmails': registeredEmails, 'contactList': contactsRich})
    else:
        return render(request, 'index.html', context={'all': all_members, 'regEmails': registeredEmails})


def ethos(request):
    return render(request, 'ethos.html', {})


def register(request):
    return render(request, 'registration/login.html')


def complete(request):
    # Handles if user goes to page without posting a request.
    if request.method == "POST":
        user = request.user
        info = request.POST.copy()
        info["User"] = user
        form = MemberForm(info)
        # form = MemberForm(request.POST or None)
        # Only saves to table if fields are valid.
        if form.is_valid():
            # Checking if both emails match before saving the user's profile
            if request.user.email == request.POST['email']:
                # Emails match
                form.save()
            else:
                messages.success(request, ('Emails do not match! Are you sure emails are the same'))
                return redirect('index')

        else:
            # Ensuring that if form isn't valid, message will be displayed and all form data  isn't erased.
            phoneNumber = request.POST['phoneNumber']
            firstName = request.POST['firstName']
            lastName = request.POST['lastName']
            jobDesc = request.POST['jobDesc']
            email = request.POST['email']
            yearsExperience = request.POST['yearsExperience']

            messages.success(request, (
                'Problem completing registration, are you sure you have not already registered using this phone number?'))
            return render(request, 'complete.html', {
                'phoneNumber': phoneNumber,
                'firstName': firstName,
                'lastName': lastName,
                'jobDesc': jobDesc,
                'email': email,
                'yearsExperience': yearsExperience,
            })
        messages.success(request, ('You have completed registration!'))
        return redirect('index')
    else:
        #            raise ValidationError(_('Invalid value'), code='invalid')
        #            return render(request, 'complete.html', {})
        return render(request, 'complete.html', {})


# Uploading our csv file (member contact list)
def uploadCSV(request):
    # Creating a form to handle the post request and sending of our csv file.
    form = CSVForm(request.POST or None, request.FILES or None)
    phoneNumUser = request.user.member.phoneNumber
    if form.is_valid():
        ContactList = form.save()
        form = CSVForm()
        # Redundant code for our usage as this will return more than one objects, solution
        # obj = CSV.objects.get(validated=False)
        with open(ContactList.file_name.path, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                # Skips the first row of column headers.
                if i == 0:
                    pass
                # From the CSV data we are creating a new record using the get or create method.
                # We use this to keep data integrity, as we don't want duplicate records.
                else:
                    GlobalContactList.objects.get_or_create(
                        phoneNumber=row[0],
                        firstName=row[1],
                        lastName=row[2]
                    )
                # Checking if a member exists with the imported phone number and then creating a record that links
                # the Member to their Contact.

                if Member.objects.filter(phoneNumber=row[0]).exists():
                    MemberContactList.objects.get_or_create(
                        Member=request.user.member,
                        contact=row[0]
                    )
            # Ensuring the validated field is satisfied so we dont get multiple objects
            # selected when uploading in the future.
            ContactList.validated = True
            ContactList.save()
            return HttpResponseRedirect(reverse('index'))
    messages.success(request,
                     'There is a problem with your contact list. Are you sure its in the correct format?')
    return render(request, 'upload.html', {'form': form})


# The function that handles finding another user's contacts within the currently authenticated user's inner circle.
def outerCircle(request, phoneNumber):
    contactOuter = phoneNumber
    userProfile = request.user.member
    inferredProfileContacts = request.user.member.phoneNumber
    #MemberContactList.objects.filter(Q(Member=userProfile) or Q(contact=inferredContacts))
    userContactsRaw = []
    outerContactsRaw = []
    if request.user.is_authenticated:
        # Retrieving full object allows us to then evaluate against onetoonefield Member... then Member's contact list.
        contactObject = Member.objects.get(phoneNumber=contactOuter)
        contactList = MemberContactList.objects.filter(Q(Member=contactObject) or (Q(contact=phoneNumber)))
        userContacts = MemberContactList.objects.filter(Member=userProfile or Q(contact=inferredProfileContacts))
        # Two lists are formed so we can conduct set operations to find mutual contacts.
        for contact in userContacts:
            userContactsRaw.append(contact.contact)
        for contact in contactList:
            outerContactsRaw.append(contact.contact)
        mutuals = list(set(userContactsRaw) & set(outerContactsRaw))
        mutualSize = len(mutuals)
        contacts = []
        contactsRich = []

        # Validation to catch if the contact hasn't imported their contacts yet (retrieving 0 values and raising a
        # mismatch error)
        if len(contactList) == 0:
            messages.success(request,
                             'Your contact has yet to import their contacts, why not send them a friendly reminder!')
            return HttpResponseRedirect(reverse('index'))
        else:
            for contact in contactList:
                contacts.append(contact)

            for contact in contacts:
                # Selecting the rest of the relevant data to the Member's contacts.
                contactPhone = contact.contact
                # Once we have the rich contact data we exclude any mutual contacts.

                contactRich = Member.objects.filter(phoneNumber=contactPhone).values('firstName', 'lastName',
                                                                                     'phoneNumber', 'jobDesc',
                                                                                     'yearsExperience').exclude(
                    phoneNumber__in=mutuals)

                contactsRich.append(contactRich)

        if request.user.is_authenticated:
            return render(request, 'outercircle.html',
                          context={'contactList': contactsRich, 'outerContact': contactObject,
                                   'mutualSize': mutualSize})


def openRequest(request, sender, mutual, requestee):
    senderObj = Member.objects.get(phoneNumber=sender)
    mutualObj = Member.objects.get(phoneNumber=mutual)
    requesteeObj = Member.objects.get(phoneNumber=requestee)

    # Creating a by default unapproved request.
    OpenRequest.objects.get_or_create(
        sender=senderObj,
        mutual=mutualObj,
        requestee=requesteeObj,
        auth1=False,
        auth2=False
    )

    print(sender, mutual, request)
    return HttpResponseRedirect(reverse('index'))


def requests(request):
    if request.user.is_authenticated:
        # Seperating types of requests.
        authUser = request.user.member
        sentRequests = OpenRequest.objects.filter(sender=authUser)
        # To store the different types of requests.
        approvedSent = []
        requestsSent = []
        for req in sentRequests:
            if req.auth1 & req.auth2:
                # Request approved from both parties.
                # Contact record created within MCL model
                MemberContactList.objects.get_or_create(
                    Member=request.user.member,
                    contact=req.requestee.phoneNumber
                )
                # Delete redundant open request object.
                OpenRequest.objects.filter(id=req.id).delete()
                print("Deleted.")
            elif req.auth1:
                approvedSent.append(req)
                print("Request Approved")
            else:
                requestsSent.append(req)
                print("Request Sent")
        # Logic for authorising initial request.
        # First stage of approval from Mutual.
        waitingApprovalM = []
        approveRequests = OpenRequest.objects.filter(mutual=authUser)
        for req in approveRequests:
            if req.auth1 & req.auth2:
                # Request approved from both parties.
                # Contact record created within MCL model
                MemberContactList.objects.get_or_create(
                    Member=req.sender,
                    contact=req.requestee.phoneNumber
                )
                # Delete redundant open request object.
                OpenRequest.objects.filter(id=req.id).delete()
                print("Deleted.")
            elif not req.auth1:
                # Requests needing user (mutual friend) approval.
                waitingApprovalM.append(req)
        # List to store requests waiting to be accepted by the requestee.
        waitingApprovalR = []
        acceptRequests = OpenRequest.objects.filter(requestee=authUser)
        for req in acceptRequests:
            if req.auth1 & req.auth2:
                # Request approved from both parties.
                # Contact record created within MCL model
                MemberContactList.objects.get_or_create(
                    Member=req.sender,
                    contact=req.requestee.phoneNumber
                )
            elif req.auth1:
                # Requests needing user (requestee) approval.
                waitingApprovalR.append(req)
        print("waitapprovalR:", waitingApprovalR)
        return render(request, 'requests.html', context={'requestsSent': requestsSent,
                                                         'waitingApprovalR': waitingApprovalR,
                                                         'waitingApprovalM': waitingApprovalM})
    else:
        return render(request, 'registration/login.html')


def deleteRequest(request, sender, requestee):
    if request.user.is_authenticated:
        OpenRequest.objects.filter(sender__phoneNumber=sender, requestee__phoneNumber=requestee).delete()
        return HttpResponseRedirect(reverse('requests'))
    else:
        return render(request, 'registration/login.html')


# Handles both authorisations and changes the boolean values
def acceptRequestAuth(request, sender, authoriser, requestee, auth):
    print(sender)
    print(authoriser)
    print(auth)
    if request.user.is_authenticated:
        if auth == "1":
            # Changes the auth1 field to True when sender and mutual contact match a record.
            acceptedRequest = OpenRequest.objects.get(sender__phoneNumber=sender, mutual__phoneNumber=authoriser)
            acceptedRequest.auth1 = 1
            acceptedRequest.save()
            return HttpResponseRedirect(reverse('requests'))
        elif auth == "2":
            # Changes the auth2 field to True when sender and requestee match a record
            acceptedRequest = OpenRequest.objects.get(sender__phoneNumber=sender, requestee__phoneNumber=requestee)
            acceptedRequest.auth2 = 1
            acceptedRequest.save()
            getRequestee = Member.objects.get(phoneNumber=requestee)

            MemberContactList.objects.get_or_create(
                Member=request.user.member,
                contact=requestee
            )
            return render(request, 'requests.html')
    else:
        return render(request, 'registration/login.html')
