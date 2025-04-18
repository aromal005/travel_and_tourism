
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('package/', views.package, name='package'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('single/<int:bid>/', views.single, name='single'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('guide/', views.guide, name='guide'),
    path('destination/', views.destination, name='destination'),
    path('package-detail/<int:pid>/', views.package_detail, name='package_detail'),
    path('profile/', views.profile, name='profile'),
    path('weather-updates/', views.weather_updates, name='weather_updates'),
    path('user-blog/', views.user_blog, name='user_blog'),
    path('add-blog/', views.add_blog, name='add_blog'),
    path("delete_blog/<int:blog_id>/", views.delete_blog, name="delete_blog"),
    path('edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:package_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path("generate_itinerary/", views.generate_ai_itinerary, name="generate_itinerary"),
    path('get_travel_news/', views.get_travel_news, name='get_travel_news'),
    path('get_travel_alerts/', views.get_travel_alerts, name='get_travel_alerts'),
    path('edit-profile/', views.edit_user_profile, name='edit_user_profile'),
    path('booking/<int:package_id>/', views.booking, name='booking'),
    # path('store-bookings/<int:package_id>/', views.store_bookings, name='store_bookings'),
    path('view-bookings/', views.view_bookings, name='view_bookings'),
    path('bookings/cancel/', views.cancel_booking, name='cancel_booking'),
    path("create-checkout-session/<int:package_id>/", views.create_checkout_session, name="create_checkout_session"),
    path("payment/success/", views.success_view, name="payment_success"),
    path("payment/cancel/", views.cancel_view, name="payment_cancel"),
    path("coupon/", views.coupon_view, name="coupon"),

    #wallet
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/withdraw/', views.withdraw_funds, name='withdraw_funds'),

    path('complaint/', views.complaint_register, name='complaint_register'),
    path('user_complaint/', views.user_complaint_view, name='user_complaint_view'),

    path('rating/', views.rating, name='rating'),
]
