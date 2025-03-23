from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('customer-management/', views.customer_management, name='customer_management'),
    path('agent-management/', views.agent_management, name='agent_management'),

]
