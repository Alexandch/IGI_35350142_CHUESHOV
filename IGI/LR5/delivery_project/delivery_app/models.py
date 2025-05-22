from decimal import ROUND_HALF_UP, Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
import re

# Валидатор возраста (18+)
def validate_age(value):
    today = timezone.now().date()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Возраст должен быть 18+.")

# Валидатор номера телефона
def validate_phone(value):
    if not re.match(r'^\+375\s\(29\)\s\d{3}-\d{2}-\d{2}$', value):
        raise ValidationError("Формат номера: +375 (29) XXX-XX-XX")

# Модель сотрудника
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    date_of_birth = models.DateField(validators=[validate_age])
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username

# Модель клиента
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone = models.CharField(max_length=20, validators=[validate_phone])
    address = models.TextField()
    date_of_birth = models.DateField(validators=[validate_age])

    def __str__(self):
        return self.user.username

# Модель вида товара
class ProductType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Название производителя")
    country = models.CharField(max_length=100, help_text="Страна производства", blank=True)

    def __str__(self):
        return self.name    

# Модель товара
class Product(models.Model):
    UNIT_CHOICES = [
        ('pieces', 'Штуки'),
        ('kg', 'Килограммы'),
        ('liters', 'Литры')
    ]
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measurement = models.CharField(max_length=20, choices=UNIT_CHOICES)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'), help_text="Вес в кг")
    stock = models.PositiveIntegerField(default=0, help_text="Количество на складе")  # Добавляем остатки

    def __str__(self):
        return self.name

class PickupPoint(models.Model):
    name = models.CharField(max_length=100, help_text="Название точки самовывоза")
    address = models.CharField(max_length=200, help_text="Адрес точки")
    working_hours = models.CharField(max_length=100, help_text="Время работы, например, '10:00-18:00'")

    def __str__(self):
        return self.name

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Уникальный код промокода")
    discount = models.DecimalField(max_digits=5, decimal_places=2, help_text="Скидка в процентах (0-100)")
    valid_from = models.DateTimeField(default=timezone.now, help_text="Дата начала действия")
    valid_to = models.DateTimeField(help_text="Дата окончания действия")
    active = models.BooleanField(default=True, help_text="Активен ли промокод")
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='promocodes', help_text="Товары, к которым применяется промокод")  # Новая связь

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'В ожидании'),
        ('Shipped', 'Отправлен'),
        ('Delivered', 'Доставлен'),
        ('Canceled', 'Отменен'),
    )
    DELIVERY_METHODS = (
        ('pickup', 'Самовывоз'),
        ('courier', 'Курьер'),
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_orders')
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    date_ordered = models.DateTimeField(auto_now_add=True)
    date_delivered = models.DateTimeField(null=True, blank=True)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='pickup')
    delivery_address = models.CharField(max_length=200, blank=True, help_text="Адрес доставки для курьера")
    promocode = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')  # Новая связь

    def __str__(self):
        return f"Заказ #{self.id} - {self.client.user.username}"

    @property
    def total_cost(self):
        base_total = sum(Decimal(str(item.quantity)) * item.price for item in self.orderitem_set.all())
        if self.promocode and self.promocode.is_valid():
            # Проверяем, применим ли промокод к товарам в заказе
            order_products = {item.product for item in self.orderitem_set.all()}
            applicable_products = set(self.promocode.applicable_products.all())
            if not applicable_products or order_products & applicable_products:  # Если промокод применим к любому товару
                discount = base_total * (self.promocode.discount / Decimal('100'))
                base_total -= discount
        total = base_total + self.delivery_cost
        # Округляем до двух знаков после запятой
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_absolute_url(self):
        return reverse('delivery_app:order_detail', kwargs={'pk': self.pk})

# Модель элемента заказа
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitem_set')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Элемент {self.product.name} в заказе #{self.order.id}"
    
    @property
    def total(self):
        return self.price * self.quantity

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.user.username})"

    class Meta:
        unique_together = ('user', 'product')  # Уникальность: один товар в корзине пользователя

class CompanyInfo(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    history = models.TextField(blank=True)
    requisites = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='article_images/', blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)  # Новая связь
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.product:
            return f"Отзыв на {self.product.name} от {self.user.username} ({self.rating})"
        return f"Отзыв от {self.user.username} ({self.rating})"