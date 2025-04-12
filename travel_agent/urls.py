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
    path('agent-profile/', views.agent_profile, name='agent_profile'),
    path('edit-agent-profile/', views.edit_agent_profile, name='edit_agent_profile'),
    path('update-fcm-token/', views.update_fcm_token, name='update_fcm_token'),
    path("get-notifications/", views.get_notifications, name="get_notifications"),
    path("send-fcm-notification/", views.send_fcm_notification, name="send_fcm_notification"),
    # path("test-fcm-token-update/", views.test_fcm_token_update, name="test-fcm-token-update"),
    path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
    path("send-push-notification/", views.send_push_notification, name="send_push_notification"),
]
