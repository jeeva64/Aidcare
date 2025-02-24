from django.urls import path
from . import views

urlpatterns=[
    path('admin_dashboard/',views.admin_panel, name='admin_panel'),
    path('admin_dashboard/approve_user/<int:user_id>',views.approve_user, name='approve_user'),
    path('admin_dashboard/reject_user/<int:user_id>',views.reject_user, name='reject_user'),
    path('admin_dashboard/contact_query',views.contact_query,name="contact_query")
]