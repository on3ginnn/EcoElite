from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('technology/', views.TechnologyView.as_view(), name='technology'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Private area (requires login)
    path('profile/', views.profile_view, name='profile'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/create/', views.create_order_view, name='create_order'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
