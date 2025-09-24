# ecoelite/core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, date
import json
from decimal import Decimal
from django.contrib.auth.views import LogoutView as DjangoLogoutView

from .models import ClientProfile, ServiceAddress, ServiceOrder, Invoice
from .forms import RegistrationForm, LoginForm, AddressForm, OrderForm


class HomeView(TemplateView):
    template_name = 'home.html'

class ServicesView(TemplateView):
    template_name = 'services.html'

class TechnologyView(TemplateView):
    template_name = 'technology.html'

class PrivacyView(TemplateView):
    template_name = 'privacy.html'

class ContactView(TemplateView):
    template_name = 'contact.html'

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            ClientProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone']
            )
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.email}!')
                return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile_view(request):
    client_profile = get_object_or_404(ClientProfile, user=request.user)
    addresses = client_profile.addresses.all()
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.client = client_profile
            address.save()
            messages.success(request, 'Адрес успешно добавлен!')
            return redirect('profile')
    else:
        form = AddressForm()
    
    return render(request, 'profile.html', {
        'client_profile': client_profile,
        'addresses': addresses,
        'form': form
    })

@login_required
def orders_view(request):
    client_profile = get_object_or_404(ClientProfile, user=request.user)
    orders = client_profile.orders.all()
    return render(request, 'orders.html', {'orders': orders})

@login_required
def create_order_view(request):
    client_profile = get_object_or_404(ClientProfile, user=request.user)
    
    if request.method == 'POST':
        form = OrderForm(client_profile, request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client_profile
            order.total_amount = Decimal('15000.00')  # Базовая цена, можно сделать динамической
            order.save()
            
            # Создаем счет для заказа
            Invoice.objects.create(order=order, amount=order.total_amount)
            
            messages.success(request, f'Заказ #{order.order_number} успешно создан!')
            return redirect('orders')
    else:
        form = OrderForm(client_profile)
    
    return render(request, 'create_order.html', {'form': form})

@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(ServiceOrder, order_number=order_number, client__user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def get_available_times(request):
    if request.method == 'GET' and request.GET.get('date'):
        selected_date = request.GET.get('date')
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # Здесь можно добавить логику проверки занятых временных слотов
            available_times = ['09:00', '11:00', '13:00', '15:00', '17:00']
            return JsonResponse({'times': available_times})
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
    return JsonResponse({'error': 'No date provided'}, status=400)


class CustomLogoutView(DjangoLogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)
    
    def get_next_page(self):
        return reverse_lazy('home')