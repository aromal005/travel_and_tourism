from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('customer-management/', views.customer_management, name='customer_management'),
    path('agent-management/', views.agent_management, name='agent_management'),
    path('toggle-agent-status/', views.toggle_agent_status, name='toggle_agent_status'),
    path('notification/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('complaints/', views.complaint_view, name='complaint_view'),
    path('send-message/', views.send_message, name='send_message'),
    path('commission-report/', views.commission_report, name='commission_report'),

]
