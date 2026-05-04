from django.urls import path
from . import views

urlpatterns = [
    path('',                                 views.home,            name='home'),
    path('search/',                          views.search_parking,  name='search'),
    path('lot/<int:lot_id>/',                views.lot_detail,      name='lot_detail'),
    path('book/<int:slot_id>/',              views.book_slot,       name='book_slot'),
    path('payment/<int:booking_id>/',        views.payment_page,    name='payment_page'),
    path('process-payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('my-bookings/',                     views.my_bookings,     name='my_bookings'),
    path('profile/',                         views.profile_view,    name='profile'),
    path('cancel/<int:booking_id>/',         views.cancel_booking,  name='cancel_booking'),
    path('extend/<int:booking_id>/',         views.extend_booking,  name='extend_booking'),
    path('register/',                        views.register_view,   name='register'),
    path('login/',                           views.login_view,      name='login'),
    path('logout/',                          views.logout_view,     name='logout'),
]