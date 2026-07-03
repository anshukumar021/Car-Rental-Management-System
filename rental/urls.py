from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.front_page_view, name='home'),
    path('about/', views.about_page_view, name='about'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset paths (OTP Flow)
    path('password-reset/', views.password_reset_otp_request_view, name='password_reset'),
    path('password-reset/verify/', views.password_reset_otp_verify_view, name='password_reset_verify'),
    path('password-reset/change/', views.password_reset_otp_change_view, name='password_reset_change'),
    
    # Vehicle inventory paths
    path('cars/', views.car_list_view, name='car_list'),
    path('cars/add/', views.car_create_view, name='car_create'),
    path('cars/<int:pk>/', views.car_detail_view, name='car_detail'),
    path('cars/<int:pk>/edit/', views.car_update_view, name='car_update'),
    path('cars/<int:pk>/delete/', views.car_delete_view, name='car_delete'),
    path('cars/<int:pk>/status/<str:status>/', views.update_car_status_view, name='update_car_status'),
    
    # Category paths
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/add/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update_view, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
    
    # Customer actions
    path('search/', views.car_list_view, name='search_car'),
    path('book/', views.book_car_view, name='book_car'),
    path('history/', views.view_history_view, name='view_history'),
    path('invoice/<int:booking_id>/', views.download_invoice_view, name='download_invoice'),
    path('bookings/<int:pk>/', views.booking_detail_view, name='booking_detail'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    path('bookings/<int:pk>/modify/', views.modify_booking_view, name='modify_booking'),
    path('bookings/<int:pk>/pickup/', views.pickup_booking_view, name='pickup_booking'),
    path('bookings/<int:pk>/return/', views.return_booking_view, name='return_booking'),
    path('bookings/<int:pk>/complete/', views.complete_booking_view, name='complete_booking'),
    path('bookings/<int:pk>/approve/', views.approve_booking_view, name='approve_booking'),
    path('admin-dashboard/users/', views.admin_users_view, name='admin_users'),
    path('admin-dashboard/bookings/', views.admin_bookings_view, name='admin_bookings'),
    path('admin-dashboard/payments/', views.admin_payments_view, name='admin_payments'),
    path('admin-dashboard/reports/', views.admin_reports_view, name='admin_reports'),
    path('bookings/<int:booking_id>/pay/', views.collect_payment_view, name='collect_payment'),
    path('payments/history/', views.payment_history_view, name='payment_history'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-dashboard/customers/', views.admin_customers_view, name='admin_customers'),
    path('admin-dashboard/customers/<int:user_id>/', views.customer_detail_admin_view, name='customer_detail_admin'),
    path('admin-dashboard/customers/<int:user_id>/verify-license/', views.verify_license_view, name='verify_license'),
    path('admin-dashboard/maintenance/', views.admin_maintenance_view, name='admin_maintenance'),
    path('admin-dashboard/maintenance/<int:pk>/edit/', views.maintenance_update_view, name='maintenance_update'),
    path('bookings/<int:pk>/reminder/rental/', views.send_rental_reminder_view, name='send_rental_reminder'),
    path('bookings/<int:pk>/reminder/return/', views.send_return_reminder_view, name='send_return_reminder'),
    path('bookings/<int:pk>/reminder/payment/', views.send_payment_reminder_view, name='send_payment_reminder'),
    path('bookings/<int:booking_id>/review/', views.submit_review_view, name='submit_review'),
]
