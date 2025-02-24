from django.urls import path
from django.contrib import admin
from . import views

urlpatterns=[
    path('',views.home,name="home"),
    path('about',views.about,name="about"),
    path('contact',views.contact,name="contact"),
    path('privacy',views.privacy,name="privacy"),
    path('error',views.error_page, name="error_page"),
]