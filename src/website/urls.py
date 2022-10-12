from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#TemplateView.as_view(template_name='index.html')
urlpatterns = [
    path('', views.index, name='index'),
    path('ethos', views.ethos, name='ethos'),
    path('requests', views.requests, name='requests'),
    path('complete', views.complete, name='complete'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path('importcontacts', views.uploadCSV, name='import-contacts'),
    path('outerCircle/<phoneNumber>', views.outerCircle, name='outerCircle'),
    path('openRequest/<sender>/<mutual>/<requestee>', views.openRequest, name='openRequest'),
    path('deleteRequest/<sender>/<requestee>', views.deleteRequest, name='deleteRequest'),
    path('acceptRequestAuth/<sender>/<authoriser>/<requestee>/<auth>', views.acceptRequestAuth, name='acceptRequestAuth')
]
