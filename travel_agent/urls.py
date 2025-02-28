from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='travel_agent_home'),
    path('Create_package/', views.create_package, name='create_package'),
    path('manage_package/', views.manage_package, name='manage_package'),
    path('edit_package/<int:pid>/', views.edit_package, name='edit_package'),
    path('delete_package/<int:id>/', views.delete_package, name='delete_package'),
    path('view-booking/', views.view_booking, name='view_booking'),
    path('category/', views.category, name='category'),
    path('create-category/', views.create_category, name='create_category'),
    path('complaint/', views.complaint, name='complaint'),
    path('payment/', views.view_payment, name='payment'),
     
]
