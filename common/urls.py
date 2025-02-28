from django.urls import path
from .views import register_user, register_travel_agent, login_view, logout_view

urlpatterns = [
    path('register/user/', register_user, name='register_user'),
    path('register/travel-agent/', register_travel_agent, name='register_travel_agent'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  
    
]
