from django.urls import path
from . import views

urlpatterns=[
    path('donor_dashboard', views.donor_dashboard, name='donor_dashboard'),
    path('donor_dashboard/add_item',views.add_item,name="add_item"),
    path('donor_dashboard/donate/<int:post_id>/<int:trust_id>',views.donate,name="donate"),
    path('donor_dashboard/view_inventory',views.inventory,name="inventory"),
    path('donor_dashboard/view_donation_history',views.donation_history,name="donation_history"),
    path('donor_dashboard/delete_inventory/<int:id>',views.delete_inventory,name="delete_inventory"),
]