from django.urls import path
from . import views

urlpatterns=[
    path('register',views.register,name="register"),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('login/',views.login,name="login"),
    path('logout',views.logout,name="logout"),
]