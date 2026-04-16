from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth
    # Landing Page
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='marketplace/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard-redirect/', views.dashboard_redirect, name='dashboard_redirect'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='marketplace/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='marketplace/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='marketplace/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='marketplace/password_reset_complete.html'), name='password_reset_complete'),

    # Seller Dashboard
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add/', views.add_ev, name='add_ev'),
    path('seller/listings/', views.seller_ev_list, name='seller_ev_list'),
    path('seller/inbox/', views.seller_inbox, name='seller_inbox'),
    path('seller/edit/<int:pk>/', views.edit_ev, name='edit_ev'),
    path('seller/delete/<int:pk>/', views.delete_ev, name='delete_ev'),
    path('seller/upload-csv/<int:pk>/', views.upload_battery_csv, name='upload_battery_csv'),
    path('seller/purchase/confirm/<int:pk>/', views.seller_confirm_sale, name='seller_confirm_sale'),
    path('seller/purchase/reject/<int:pk>/', views.seller_reject_sale, name='seller_reject_sale'),

    # Buyer Dashboard
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/inbox/', views.buyer_inbox, name='buyer_inbox'),
    path('message/reply/<int:pk>/', views.reply_message, name='reply_message'),
    path('ev/<int:pk>/', views.ev_detail, name='ev_detail'),
    path('ev/<int:pk>/check-health/', views.check_battery_health, name='check_battery_health'),
    path('battery-health/', views.battery_health_center, name='battery_health_center'),
    path('contact-admin/', views.contact_admin, name='contact_admin'),

    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/inbox/', views.admin_inbox, name='admin_inbox'),
    path('admin-dashboard/approve-ev/<int:pk>/', views.approve_ev, name='approve_ev'),
    path('admin-dashboard/reject-ev/<int:pk>/', views.reject_ev, name='reject_ev'),
    path('admin-dashboard/approve-user/<int:pk>/', views.approve_user, name='approve_user'),
    path('admin-dashboard/block-user/<int:pk>/', views.block_user, name='block_user'),

    # Purchase Flow
    path('ev/<int:pk>/purchase/', views.submit_purchase_request, name='submit_purchase_request'),
    path('admin-dashboard/purchase/review/<int:pk>/', views.admin_review_purchase, name='admin_review_purchase'),
    path('admin-dashboard/purchase/invoice/<int:pk>/', views.admin_generate_invoice, name='admin_generate_invoice'),
    path('buyer/purchase/pay/<int:pk>/', views.buyer_submit_payment, name='buyer_submit_payment'),
    path('admin-dashboard/purchase/confirm-payment/<int:pk>/', views.admin_confirm_payment, name='admin_confirm_payment'),
    path('admin-dashboard/purchase/confirm/<int:pk>/', views.confirm_purchase, name='confirm_purchase'),
    path('admin-dashboard/purchase/reject/<int:pk>/', views.reject_purchase, name='reject_purchase'),
]
