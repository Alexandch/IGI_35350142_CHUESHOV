# delivery_app/tests.py
from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
import re

from .models import (
    Employee, Client, ProductType, Manufacturer, Product, PickupPoint, PromoCode,
    Order, OrderItem, CartItem, CompanyInfo, Article, FAQ, Vacancy, Review
)
from .models import validate_age, validate_phone

class ModelTests(TestCase):
    def setUp(self):
        # Создаём тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.employee_user = User.objects.create_user(username='employee', password='emppass123')
        self.client_user = User.objects.create_user(username='client', password='clientpass123')

        # Создаём сотрудника
        self.employee = Employee.objects.create(
            user=self.employee_user,
            date_of_birth=date(1990, 1, 1),
            position='Manager'
        )

        # Создаём клиента
        self.test_client = Client.objects.create(
            user=self.client_user,
            phone='+375 (29) 123-45-67',
            address='Minsk, Test St. 1',
            date_of_birth=date(2000, 1, 1)
        )

        # Создаём тип продукта и производителя
        self.product_type = ProductType.objects.create(name='Fruits')
        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer', country='Belarus')

        # Создаём продукт
        self.product = Product.objects.create(
            name='Apple',
            price=Decimal('1.99'),
            unit_of_measurement='kg',
            product_type=self.product_type,
            manufacturer=self.manufacturer,
            weight=Decimal('1.00'),
            stock=100
        )

        # Создаём точку самовывоза
        self.pickup_point = PickupPoint.objects.create(
            name='Minsk Pickup',
            address='Minsk, Pickup St. 1',
            working_hours='10:00-18:00'
        )

        # Создаём промокод
        self.promocode = PromoCode.objects.create(
            code='TEST10',
            discount=Decimal('10.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=1),
            active=True
        )
        self.promocode.applicable_products.add(self.product)

    def test_validate_age_under_18(self):
        """Тест валидатора возраста: должен отклонять пользователей младше 18 лет"""
        under_18_date = date.today() - timedelta(days=17 * 365)
        with self.assertRaises(ValidationError):
            validate_age(under_18_date)

    def test_validate_age_over_18(self):
        """Тест валидатора возраста: должен принимать пользователей старше 18 лет"""
        over_18_date = date(2000, 1, 1)
        try:
            validate_age(over_18_date)
        except ValidationError:
            self.fail("validate_age() raised ValidationError unexpectedly!")

    def test_validate_phone_correct_format(self):
        """Тест валидатора телефона: корректный формат"""
        valid_phone = '+375 (29) 123-45-67'
        try:
            validate_phone(valid_phone)
        except ValidationError:
            self.fail("validate_phone() raised ValidationError unexpectedly!")

    def test_validate_phone_incorrect_format(self):
        """Тест валидатора телефона: некорректный формат"""
        invalid_phone = '123456789'
        with self.assertRaises(ValidationError):
            validate_phone(invalid_phone)

    def test_order_total_cost_with_promocode(self):
        """Тест расчёта общей стоимости заказа с промокодом"""
        order = Order.objects.create(
            client=self.test_client,
            employee=self.employee,
            pickup_point=self.pickup_point,
            status='Pending',
            delivery_cost=Decimal('0.00'),
            delivery_method='pickup',
            promocode=self.promocode
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=Decimal('2.00'),
            price=self.product.price
        )
        # Базовая стоимость: 2 * 1.99 = 3.98
        # Промокод: 10% скидка => 3.98 * 0.1 = 0.398 => 3.98 - 0.398 = 3.582
        # После округления: 3.58
        expected_total = Decimal('3.58')
        self.assertEqual(order.total_cost, expected_total)

    def test_promocode_is_valid(self):
        """Тест проверки валидности промокода"""
        self.assertTrue(self.promocode.is_valid())

    def test_promocode_expired(self):
        """Тест просроченного промокода"""
        expired_promocode = PromoCode.objects.create(
            code='EXPIRED',
            discount=Decimal('5.00'),
            valid_from=timezone.now() - timedelta(days=10),
            valid_to=timezone.now() - timedelta(days=1),
            active=True
        )
        self.assertFalse(expired_promocode.is_valid())

class ViewTests(TestCase):
    def setUp(self):
        self.test_client = TestClient()
        # Создаём пользователей
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass123')
        self.employee_user = User.objects.create_user(username='employee', password='emppass123')
        self.client_user = User.objects.create_user(username='client', password='clientpass123')

        # Создаём сотрудника
        self.employee = Employee.objects.create(
            user=self.employee_user,
            date_of_birth=date(1990, 1, 1),
            position='Manager'
        )

        # Создаём клиента
        self.test_client_model = Client.objects.create(
            user=self.client_user,
            phone='+375 (29) 123-45-67',
            address='Minsk, Test St. 1',
            date_of_birth=date(2000, 1, 1)
        )

        # Создаём тип продукта и продукт
        self.product_type = ProductType.objects.create(name='Fruits')
        self.product = Product.objects.create(
            name='Apple',
            price=Decimal('1.99'),
            unit_of_measurement='kg',
            product_type=self.product_type,
            stock=100
        )

        # Создаём точку самовывоза
        self.pickup_point = PickupPoint.objects.create(
            name='Minsk Pickup',
            address='Minsk, Pickup St. 1',
            working_hours='10:00-18:00'
        )

        # Создаём заказ
        self.order = Order.objects.create(
            client=self.test_client_model,
            employee=self.employee,
            pickup_point=self.pickup_point,
            status='Pending',
            delivery_cost=Decimal('0.00'),
            delivery_method='pickup'
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=Decimal('2.00'),
            price=self.product.price
        )

    def test_employee_panel_superuser_access(self):
        """Тест доступа суперпользователя к панели сотрудника"""
        self.test_client.login(username='admin', password='adminpass123')
        # Создаём профиль Employee для суперпользователя
        Employee.objects.create(
            user=self.superuser,
            date_of_birth=date(1990, 1, 1),
            position='Admin'
        )
        response = self.test_client.get(reverse('delivery_app:employee_panel'))
        self.assertEqual(response.status_code, 200)
        # Проверяем, что суперпользователь видит хотя бы один заказ
        self.assertGreaterEqual(len(response.context['orders']), 1)

    def test_employee_panel_employee_access(self):
        """Тест доступа обычного сотрудника к панели сотрудника"""
        self.test_client.login(username='employee', password='emppass123')
        response = self.test_client.get(reverse('delivery_app:employee_panel'))
        self.assertEqual(response.status_code, 200)
        # Проверяем, что сотрудник видит только свои заказы
        self.assertEqual(len(response.context['orders']), 1)

    def test_employee_panel_no_access(self):
        """Тест доступа клиента к панели сотрудника"""
        self.test_client.login(username='client', password='clientpass123')
        response = self.test_client.get(reverse('delivery_app:employee_panel'))
        self.assertRedirects(response, reverse('delivery_app:home'))

    def test_order_list_view_client(self):
        """Тест доступа клиента к списку заказов"""
        self.test_client.login(username='client', password='clientpass123')
        response = self.test_client.get(reverse('delivery_app:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 1)

    def test_order_detail_view_employee(self):
        """Тест доступа сотрудника к деталям заказа"""
        self.test_client.login(username='employee', password='emppass123')
        response = self.test_client.get(reverse('delivery_app:order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], self.order)

    def test_login_view_redirect(self):
        """Тест перенаправления неавторизованного пользователя на страницу логина"""
        response = self.test_client.get(reverse('delivery_app:add_to_cart', args=[self.product.id]), follow=True)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('delivery_app:add_to_cart', args=[self.product.id])}")

class CartTests(TestCase):
    def setUp(self):
        self.test_client = TestClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.product_type = ProductType.objects.create(name='Fruits')
        self.product = Product.objects.create(
            name='Apple',
            price=Decimal('1.99'),
            unit_of_measurement='kg',
            product_type=self.product_type,
            stock=100
        )

    def test_add_to_cart(self):
        """Тест добавления товара в корзину"""
        self.test_client.login(username='testuser', password='testpass123')
        response = self.test_client.post(reverse('delivery_app:add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        cart_item = CartItem.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.total_price, Decimal('3.98'))