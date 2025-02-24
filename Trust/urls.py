from django.urls import path
from . import views

urlpatterns=[
    path('trust_dashboard', views.trust_dashboard, name='trust_dashboard'),
    path('trust_dashboard/create_post/', views.create_post, name='create_post'),
    path('trust_dashboard/delete_post/<int:post_id>', views.delete_post, name='delete_post'),
    path('trust_dashboard/view_request',views.view_request,name="view_request"),
    path('trust_dashboard/approve_request/<int:request_id>',views.approve_request,name="approve_request"),
    path('trust_dashboard/reject_request/<int:request_id>',views.reject_request,name="reject_request"),
]