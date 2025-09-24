from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Профили клиентов'
    
    def __str__(self):
        return f"{self.user.email} ({self.phone})"


class ServiceAddress(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='addresses')
    address = models.TextField(verbose_name='Адрес')
    is_primary = models.BooleanField(default=False, verbose_name='Основной адрес')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Адрес обслуживания'
        verbose_name_plural = 'Адреса обслуживания'
    
    def __str__(self):
        return f"{self.address}"


class ServiceOrder(models.Model):
    STATUS_NEW = 'new'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_CONFIRMED, 'Подтвержден'),
        (STATUS_IN_PROGRESS, 'Выполняется'),
        (STATUS_COMPLETED, 'Завершен'),
        (STATUS_CANCELLED, 'Отменен'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Номер заказа')
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(ServiceAddress, on_delete=models.CASCADE, verbose_name='Адрес обслуживания')
    service_date = models.DateField(verbose_name='Дата обслуживания')
    service_time = models.TimeField(verbose_name='Время обслуживания')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name='Статус')
    notes = models.TextField(blank=True, verbose_name='Примечания клиента')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Заказ услуги'
        verbose_name_plural = 'Заказы услуг'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"EE{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Заказ {self.order_number} - {self.client}"


class Invoice(models.Model):
    order = models.OneToOneField(ServiceOrder, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=20, unique=True, verbose_name='Номер счета')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Сумма')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')
    
    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Счет {self.invoice_number} - {self.order}"