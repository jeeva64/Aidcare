from django.urls import path
from . import views

urlpatterns=[
    path('admin_dashboard/',views.admin_panel, name='admin_panel'),
    
    path('admin_dashboard/approve_user/<int:user_id>/<str:username>/<str:email>/',views.approve_user, name='approve_user'),
    path('admin_dashboard/reject_user/<int:user_id>',views.reject_user, name='reject_user'),
    
    path('admin_dashboard/contact_query',views.contact_query,name="contact_query"),
    path('admin_dashboard/contact_query/delete/<int:contact_id>',views.delete_contact,name="delete_contact"),
    
    path('admin_dashboard/view_user',views.view_user,name="view_user"),
    path('admin_dashboard/insert_user',views.insert_user,name="insert_user"),
    path('admin_dashboard/update_user/<int:user_id>',views.update_user,name="update_user"),
    path('admin_dashboard/delete_user/<int:user_id>',views.delete_user,name="delete_user"),
]