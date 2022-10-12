from django.contrib import admin
from .models import Member
from .models import CSV
from .models import GlobalContactList, MemberContactList, OpenRequest
# Register your models here.
admin.site.register(Member)
admin.site.register(CSV)
admin.site.register(MemberContactList)
admin.site.register(GlobalContactList)
admin.site.register(OpenRequest)