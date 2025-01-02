from django.urls import path
from django.contrib import admin
from . import views
from App.views import admin_panel, approve_user
urlpatterns=[
    path('home',views.home,name="home"),
    path('register',views.register,name="register"),
    path('login/',views.login,name="login"),
     path('logout',views.logout,name="logout"),
    path('about',views.about,name="about"),

    path('donor_dashboard', views.donor_dashboard, name='donor_dashboard'),
    path('trust_dashboard', views.trust_dashboard, name='trust_dashboard'),

    path('donor_dashboard/add_item',views.add_item,name="add_item"),
    path('donor_dashboard/inventory',views.inventory,name="inventory"),
    path('donor_dashboard/delete_inventory/<int:id>',views.delete_inventory,name="delete_inventory"),

    path('mark_as_donated/<int:item_id>',views.mark_as_donated,name="mark_as_donated"),
    path('trust_dashboard/create_post/', views.create_post, name='create_post'),
    path('trust_dashboard/delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
]