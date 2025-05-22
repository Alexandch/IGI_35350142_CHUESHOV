from decimal import Decimal
import logging
import statistics
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth import login
from django.shortcuts import redirect
from django.db.models import Q
import calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import requests
from .models import FAQ, Article, CompanyInfo, Manufacturer, PickupPoint, Review, Vacancy, CartItem
from delivery_app.forms import ClientForm, CustomUserCreationForm, ReviewForm
from .models import Employee, Product, Order, OrderItem, Client, ProductType, PromoCode
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings

# Представление списка продуктов
class ProductListView(ListView):
    model = Product
    template_name = 'delivery_app/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        type_filter = self.request.GET.get('type_filter')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if type_filter:
            queryset = queryset.filter(product_type__name=type_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = ProductType.objects.all()
        context['current_date'] = timezone.now().strftime('%d/%m/%Y')
        context['timezone'] = 'Europe/Minsk'
        context['calendar'] = calendar.monthcalendar(timezone.now().year, timezone.now().month)
        return context

# Представление деталей заказа (для сотрудников или клиентов)
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'delivery_app/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'client_profile'):
            return Order.objects.filter(client=user.client_profile)
        elif hasattr(user, 'employee_profile'):
            return Order.objects.filter(employee=user.employee_profile)
        return Order.objects.none()

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        order = self.get_object()
        user = request.user
        if (hasattr(user, 'client_profile') and order.client != user.client_profile) or \
           (hasattr(user, 'employee_profile') and order.employee != user.employee_profile):
            raise PermissionDenied("У вас нет прав для просмотра этого заказа.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().strftime('%d/%m/%Y')
        context['timezone'] = 'Europe/Minsk'
        context['calendar'] = calendar.monthcalendar(timezone.now().year, timezone.now().month)
        return context

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для просмотра этого заказа.")

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'delivery_app/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()  # Суперпользователь видит все заказы
        try:
            employee = Employee.objects.get(user=user)
            return Order.objects.filter(employee=employee)  # Сотрудник видит свои заказы
        except Employee.DoesNotExist:
            try:
                client = Client.objects.get(user=user)
                return Order.objects.filter(client=client)  # Клиент видит свои заказы
            except Client.DoesNotExist:
                return Order.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().strftime('%d/%m/%Y')
        context['timezone'] = 'Europe/Minsk'
        context['calendar'] = calendar.monthcalendar(timezone.now().year, timezone.now().month)
        return context
    
# Простая главная страница (для примера)
def home_view(request):
    latest_order = Order.objects.order_by('-date_ordered').first()
    context = {
        'latest_order': latest_order,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/home.html', context)

def custom_logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logout

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('delivery_app:home')
    else:
        form = AuthenticationForm()
    return render(request, 'delivery_app/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('delivery_app:home')
    return redirect('delivery_app:home')

@login_required
def create_order(request):
    # Получаем клиента, связанного с текущим пользователем
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, "Клиентский профиль не найден. Обратитесь к администратору.")
        return redirect('delivery_app:home')

    products = Product.objects.all()  # Получаем все доступные продукты

    if request.method == 'POST':
        # Создаем новый заказ
        order = Order.objects.create(client=client, status='Pending')

        # Обрабатываем выбранные продукты и их количество
        for product in products:
            quantity = request.POST.get(f'quantity_{product.id}', '0')
            try:
                quantity = float(quantity)
            except ValueError:
                quantity = 0

            if quantity > 0:
                # Создаем элемент заказа
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price  # Цена фиксируется на момент создания заказа
                )

        if order.orderitem_set.exists():
            messages.success(request, "Заказ успешно создан!")
            return redirect('delivery_app:order_detail', pk=order.id)
        else:
            order.delete()  # Удаляем пустой заказ
            messages.error(request, "Вы не выбрали ни одного товара.")
            return redirect('delivery_app:create_order')

    # Добавляем контекст для отображения текущей даты и календаря (для соответствия остальным представлениям)
    context = {
        'products': products,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
        'calendar': calendar.monthcalendar(timezone.now().year, timezone.now().month),
    }
    return render(request, 'delivery_app/create_order.html', context)

@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    # Проверяем доступ
    user = request.user
    if not (user.is_superuser or (hasattr(user, 'employee') and order.employee == user.employee)):
        messages.error(request, "У вас нет прав для редактирования этого заказа.")
        return redirect('delivery_app:order_detail', pk=pk)

    products = Product.objects.all()

    if request.method == 'POST':
        # Обновляем статус
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES).keys():
            order.status = status
            order.save()

        # Обновляем элементы заказа
        order.orderitem_set.all().delete()  # Удаляем старые элементы
        for product in products:
            quantity = request.POST.get(f'quantity_{product.id}', '0')
            try:
                quantity = float(quantity)
            except ValueError:
                quantity = 0

            if quantity > 0:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

        messages.success(request, "Заказ успешно обновлен!")
        return redirect('delivery_app:order_detail', pk=pk)

    context = {
        'order': order,
        'products': products,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
        'calendar': calendar.monthcalendar(timezone.now().year, timezone.now().month),
    }
    return render(request, 'delivery_app/edit_order.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите, чтобы добавить товар в корзину.")
        return redirect('delivery_app:login')

    quantity = int(request.POST.get('quantity', 1))  # Получаем количество из формы, по умолчанию 1
    if quantity < 1:
        messages.error(request, "Количество должно быть больше 0.")
        return redirect('delivery_app:product_list')

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()
    messages.success(request, f"{product.name} добавлен в корзину.")
    return redirect('delivery_app:cart')

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)

    current_date = timezone.now()
    year = current_date.year
    month = current_date.month
    calendar_data = calendar.monthcalendar(year, month)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'current_date': current_date,
        'timezone': timezone.get_current_timezone_name(),
        'calendar': calendar_data,
    }
    return render(request, 'delivery_app/cart.html', context)

@login_required
def update_cart(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            quantity_key = f'quantity_{item.id}'
            if quantity_key in request.POST:
                try:
                    new_quantity = int(request.POST[quantity_key])
                    if new_quantity < 1:
                        messages.error(request, f"Количество для {item.product.name} должно быть больше 0.")
                        continue
                    item.quantity = new_quantity
                    item.save()
                except ValueError:
                    messages.error(request, f"Некорректное количество для {item.product.name}.")
        messages.success(request, "Корзина обновлена.")
    return redirect('delivery_app:cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Товар удалён из корзины.")
    return redirect('delivery_app:cart')

@login_required
def checkout(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        logger.error(f"Клиентский профиль для {request.user.username} не найден")
        messages.error(request, "Клиентский профиль не найден. Обратитесь к администратору.")
        return redirect('delivery_app:home')

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        logger.warning(f"Корзина пуста для {request.user.username}")
        messages.error(request, "Корзина пуста.")
        return redirect('delivery_app:cart')

    employees = Employee.objects.all()
    current_employee = None
    try:
        current_employee = Employee.objects.get(user=request.user)
        employees = employees.exclude(user=request.user)
    except Employee.DoesNotExist:
        pass

    discount = Decimal('0')
    promo_code = None
    selected_delivery_method = request.POST.get('delivery_method', 'pickup') if request.method == 'POST' else 'pickup'
    selected_pickup_point = request.POST.get('pickup_point', '') if request.method == 'POST' else ''
    delivery_address = request.POST.get('delivery_address', '') if request.method == 'POST' else client.address if hasattr(client, 'address') else ''

    products = Product.objects.filter(id__in=cart_items.values_list('product_id', flat=True))

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        promo_code_input = request.POST.get('promo_code', '').strip()
        pickup_point_id = request.POST.get('pickup_point')
        delivery_method = request.POST.get('delivery_method', 'pickup')
        delivery_address = request.POST.get('delivery_address', '')
        employee = None
        pickup_point = None

        if employee_id:
            employee = get_object_or_404(Employee, id=employee_id)
        if delivery_method == 'pickup' and pickup_point_id:
            pickup_point = get_object_or_404(PickupPoint, id=pickup_point_id)
        elif delivery_method == 'pickup' and not pickup_point_id:
            messages.error(request, "Выберите точку самовывоза для способа доставки 'Самовывоз'.")
            return redirect('delivery_app:checkout')
        elif delivery_method == 'courier' and not delivery_address:
            messages.error(request, "Укажите адрес доставки для способа доставки 'Курьер'.")
            return redirect('delivery_app:checkout')

        if promo_code_input:
            try:
                promo_code = PromoCode.objects.get(code=promo_code_input)
                if not promo_code.is_valid():
                    messages.error(request, "Промокод недействителен или истёк.")
                else:
                    discount = promo_code.discount
            except PromoCode.DoesNotExist:
                messages.error(request, "Промокод не найден.")

        if not messages.get_messages(request):
            for cart_item in cart_items:
                if cart_item.product.stock < cart_item.quantity:
                    messages.error(request, f"Недостаточно товара '{cart_item.product.name}' на складе. Доступно: {cart_item.product.stock}, требуется: {cart_item.quantity}.")
                    return redirect('delivery_app:checkout')

            total_weight = sum(product.weight * Decimal(cart_item.quantity) for product, cart_item in zip(products, cart_items))
            delivery_cost = Decimal('0.00')
            if delivery_method == 'courier':
                delivery_cost = Decimal('5.00') + (total_weight * Decimal('2.00'))

            order = Order.objects.create(
                client=client,
                employee=employee,
                status='Pending',
                pickup_point=pickup_point,
                delivery_method=delivery_method,
                delivery_cost=delivery_cost,
                delivery_address=delivery_address
            )
            logger.debug(f"Создан заказ #{order.id} для клиента {client.user.username}")
            total = Decimal('0')
            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity
                price = product.price * (Decimal('1') - discount / Decimal('100'))
                OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
                total += price * Decimal(quantity)
                product.stock -= quantity
                product.save()
                cart_item.delete()

            message = f"Заказ успешно создан! Общая сумма: {total + order.delivery_cost:.2f} BYN"
            if discount:
                message += f" (с учётом скидки {discount}%)"
            messages.success(request, message)
            # Убедимся, что перенаправление идёт на правильный URL
            return redirect('delivery_app:order_detail', pk=order.id)

    cart_items_list = [
        {
            'product': item.product,
            'quantity': item.quantity,
            'total': item.product.price * Decimal(item.quantity)
        }
        for item in cart_items
    ]
    total = sum(item['total'] for item in cart_items_list)

    context = {
        'cart_items': cart_items_list,
        'employees': employees,
        'pickup_points': PickupPoint.objects.all(),
        'total': total,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
        'calendar': calendar.monthcalendar(timezone.now().year, timezone.now().month),
        'delivery_methods': Order.DELIVERY_METHODS,
        'selected_delivery_method': selected_delivery_method,
        'selected_pickup_point': selected_pickup_point,
        'delivery_address': delivery_address,
    }
    return render(request, 'delivery_app/checkout.html', context)

def profile(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        client = Client(user=request.user)

    country_info = None
    try:
        country_response = requests.get('https://restcountries.com/v3.1/name/Belarus')
        country_info = country_response.json()[0]
    except:
        pass

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect('delivery_app:profile')
    else:
        form = ClientForm(instance=client, user=request.user)

    context = {
        'form': form,
        'country_info': country_info,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
        'calendar': calendar.monthcalendar(timezone.now().year, timezone.now().month),
    }
    return render(request, 'delivery_app/profile.html', context)

logger = logging.getLogger('delivery_app')

def employee_panel(request):
    logger.debug(f"Запрос на панель сотрудника от {request.user.username}")
    try:
        employee = Employee.objects.get(user=request.user)
        logger.debug(f"Сотрудник найден: {employee}")
    except Employee.DoesNotExist:
        logger.error(f"Пользователь {request.user.username} не является сотрудником")
        messages.error(request, "У вас нет прав доступа к панели сотрудников.")
        return redirect('delivery_app:home')

    # Фильтрация заказов: все заказы для superuser, только свои для обычных сотрудников
    if request.user.is_superuser:
        orders = Order.objects.all()
        logger.debug("Суперпользователь: отображаются все заказы")
    else:
        orders = Order.objects.filter(employee=employee)
        logger.debug(f"Обычный сотрудник: отображаются только заказы сотрудника {employee}")

    status_filter = request.GET.get('status_filter')
    date_filter = request.GET.get('date_filter')
    type_filter = request.GET.get('type_filter')
    delivery_method_filter = request.GET.get('delivery_method_filter')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if date_filter:
        orders = orders.filter(date_ordered__date=date_filter)
    if type_filter:
        orders = orders.filter(orderitem__product__product_type__name=type_filter)
    if delivery_method_filter:
        orders = orders.filter(delivery_method=delivery_method_filter)
    orders = orders.order_by('-date_ordered')
    logger.debug(f"Найдено заказов после фильтрации: {orders.count()}")

    orders_with_total = []
    for order in orders:
        total = sum(Decimal(str(item.price)) * Decimal(str(item.quantity)) for item in order.orderitem_set.all())
        orders_with_total.append({'order': order, 'total_cost': total})
        logger.debug(f"Заказ #{order.id} с общей стоимостью: {total}")

    total_orders = len(orders_with_total)
    status_counts = {status: len([o for o in orders_with_total if o['order'].status == status]) for status, _ in Order.STATUS_CHOICES}

    clients_alpha = Client.objects.order_by('user__username')
    total_sales = sum(o['total_cost'] for o in orders_with_total) or Decimal('0')
    logger.debug(f"Общая выручка: {total_sales}")

    sales = [o['total_cost'] for o in orders_with_total if o['total_cost']]
    sales_mean = statistics.mean(sales) if sales else Decimal('0')
    sales_median = statistics.median(sales) if sales else Decimal('0')
    sales_mode = statistics.mode(sales) if sales else Decimal('0')

    ages = []
    today = timezone.now().date()
    for client in Client.objects.exclude(date_of_birth__isnull=True):
        age = today.year - client.date_of_birth.year - ((today.month, today.day) < (client.date_of_birth.month, client.date_of_birth.day))
        if age >= 18:
            ages.append(age)
    age_mean = statistics.mean(ages) if ages else 0
    age_median = statistics.median(ages) if ages else 0

    popular_types = ProductType.objects.annotate(
        order_count=Count('products__order_items')
    ).order_by('-order_count')

    profit_by_type = ProductType.objects.annotate(
        total_profit=Sum(
            ExpressionWrapper(
                F('products__order_items__price') * F('products__order_items__quantity'),
                output_field=DecimalField()
            )
        )
    ).order_by('-total_profit')

    if request.method == 'POST':
        logger.debug(f"POST-запрос: {request.POST}")
        action = request.POST.get('action')
        if action == 'update':
            order_id = request.POST.get('order_id')
            status = request.POST.get('status')
            date_delivered = request.POST.get('date_delivered')
            order = get_object_or_404(Order, id=order_id, employee=employee)
            old_status = order.status
            if status in dict(Order.STATUS_CHOICES).keys():
                order.status = status
            if date_delivered:
                order.date_delivered = date_delivered
            order.save()
            logger.debug(f"Статус заказа #{order_id} обновлён на {status}")
            messages.success(request, f"Статус заказа #{order_id} обновлен!")

            if old_status != status:
                subject = f'Статус вашего заказа #{order.id} изменён'
                message = f'Уважаемый(ая) {order.client.user.username},\n\nСтатус вашего заказа изменён с "{old_status}" на "{status}".\n\nДетали заказа можно посмотреть здесь: {request.build_absolute_uri(order.get_absolute_url())}\n\nС уважением,\nКоманда магазина'
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.client.user.email],
                    fail_silently=True,
                )
                logger.debug(f"Email отправлен клиенту {order.client.user.email}")

        elif action == 'assign' and request.user.is_superuser:
            order_id = request.POST.get('order_id')
            employee_id = request.POST.get('employee_id')
            order = get_object_or_404(Order, id=order_id)
            order.employee = get_object_or_404(Employee, id=employee_id)
            order.save()
            logger.debug(f"Сотрудник #{employee_id} назначен на заказ #{order_id}")
            messages.success(request, f"Сотрудник назначен на заказ #{order_id}!")

        return redirect('delivery_app:employee_panel')

    employees = Employee.objects.all()
    clients = Client.objects.all()
    context = {
        'orders': orders_with_total,
        'employees': employees,
        'total_orders': total_orders,
        'status_counts': status_counts,
        'clients': clients,
        'clients_alpha': clients_alpha,
        'total_sales': total_sales,
        'sales_mean': sales_mean,
        'sales_median': sales_median,
        'sales_mode': sales_mode,
        'age_mean': age_mean,
        'age_median': age_median,
        'popular_types': popular_types,
        'profit_by_type': profit_by_type,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
        'calendar': calendar.monthcalendar(timezone.now().year, timezone.now().month),
        'status_choices': Order.STATUS_CHOICES,
        'delivery_methods': Order.DELIVERY_METHODS,
        'product_types': ProductType.objects.all(),
    }
    logger.debug(f"Контекст перед рендерингом: {context}")
    return render(request, 'delivery_app/employee_panel.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль клиента автоматически
            Client.objects.create(
                user=user,
                phone='+375 (29) 123-45-67',  # Значение по умолчанию
                address='Не указан',  # Значение по умолчанию
                date_of_birth='1990-01-01'  # Значение по умолчанию
            )
            login(request, user)  # Автоматически логиним пользователя
            messages.success(request, "Регистрация успешно завершена! Добро пожаловать!")
            return redirect('delivery_app:home')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
        'calendar': calendar.monthcalendar(timezone.now().year, timezone.now().month),
    }
    return render(request, 'delivery_app/register.html', context)

def employee_products(request):

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_product':
            product_id = request.POST.get('product_id')
            if product_id:
                product = get_object_or_404(Product, id=product_id)
                product.name = request.POST.get('name', product.name)
                product.price = request.POST.get('price', product.price)
                product.unit_of_measurement = request.POST.get('unit_of_measurement', product.unit_of_measurement)
                product.product_type_id = request.POST.get('product_type', product.product_type_id)
                product.manufacturer_id = request.POST.get('manufacturer', product.manufacturer_id)
                product.save()
                messages.success(request, "Товар обновлён!")
            else:
                name = request.POST.get('name')
                price = request.POST.get('price')
                unit_of_measurement = request.POST.get('unit_of_measurement')
                product_type_id = request.POST.get('product_type')
                manufacturer_id = request.POST.get('manufacturer')
                Product.objects.create(
                    name=name, price=price, unit_of_measurement=unit_of_measurement,
                    product_type_id=product_type_id, manufacturer_id=manufacturer_id
                )
                messages.success(request, "Товар добавлен!")
        elif action == 'update_product_type':
            product_type_id = request.POST.get('product_type_id')
            if product_type_id:
                product_type = get_object_or_404(ProductType, id=product_type_id)
                product_type.name = request.POST.get('name', product_type.name)
                product_type.save()
                messages.success(request, "Тип товара обновлён!")
            else:
                name = request.POST.get('name')
                ProductType.objects.create(name=name)
                messages.success(request, "Тип товара добавлен!")

    products = Product.objects.all()
    product_types = ProductType.objects.all()
    manufacturers = Manufacturer.objects.all()
    context = {
        'products': products,
        'product_types': product_types,
        'manufacturers': manufacturers,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
        'calendar': calendar.monthcalendar(timezone.now().year, timezone.now().month),
    }
    return render(request, 'delivery_app/employee_products.html', context)

logger = logging.getLogger('delivery_app')
def home_view(request):
    # Initialize data
    weather_data = {'city': 'Minsk', 'temperature': 'N/A', 'description': 'N/A'}
    exchange_data = {'usd': 'N/A', 'eur': 'N/A'}

    # Weather API
    weather_api_key = '1f7f7dc7d087585e7be226e9cd59a332'  # Replace with your key
    city = 'Minsk'
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric'
    try:
        weather_response = requests.get(weather_url, timeout=5)
        weather_response.raise_for_status()
        weather_json = weather_response.json()
        logger.debug(f"Raw weather API response: {weather_json}")
        if weather_json.get('cod') == 200:
            weather_data = {
                'city': city,
                'temperature': weather_json['main'].get('temp', 'N/A'),
                'description': weather_json['weather'][0].get('description', 'N/A'),
            }
            logger.debug(f"Processed weather data: {weather_data}")
        else:
            logger.error(f"Weather API error: {weather_json.get('message')}")
    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {e}")

    # Exchange Rate API
    exchange_api_key = '878475dc62894ca828e0708a'  # Replace with your key
    exchange_url = f'https://v6.exchangerate-api.com/v6/{exchange_api_key}/latest/BYN'
    try:
        exchange_response = requests.get(exchange_url, timeout=5)
        exchange_response.raise_for_status()
        exchange_json = exchange_response.json()
        logger.debug(f"Raw exchange API response: {exchange_json}")
        if exchange_json.get('result') == 'success':
            usd_rate = exchange_json['conversion_rates'].get('USD', 'N/A')
            eur_rate = exchange_json['conversion_rates'].get('EUR', 'N/A')

            if usd_rate != 'N/A' and eur_rate != 'N/A':
            # Инверсия курсов: 1 / (курс BYN к иностранной валюте)
                exchange_data = {
                    'usd': Decimal('1') / Decimal(str(usd_rate)),
                    'eur': Decimal('1') / Decimal(str(eur_rate)),
                }
                logger.debug(f"Processed exchange data: {exchange_data}")
            else:
                exchange_data = {
                    'usd': 'N/A',
                    'eur': 'N/A',
                }
                logger.error("Exchange API missing USD or EUR rates")
        else:
            logger.error(f"Exchange API error: {exchange_json.get('error-type')}")
            exchange_data = {
                'usd': 'N/A',
                'eur': 'N/A',
            }
    except requests.RequestException as e:
        logger.error(f"Exchange API request failed: {e}")
        exchange_data = {
            'usd': 'N/A',
            'eur': 'N/A',
        }

    # Calendar Data
    current_date = timezone.now()
    year = current_date.year
    month = current_date.month
    calendar.setfirstweekday(calendar.MONDAY)
    calendar_data = calendar.monthcalendar(year, month)
    logger.debug(f"Calendar data: {calendar_data}")

    context = {
        'current_date': current_date,
        'timezone': timezone.get_current_timezone_name(),
        'calendar': calendar_data,
        'weather_data': weather_data,
        'exchange_data': exchange_data,
    }
    logger.debug(f"Final context for home template: {context}")
    return render(request, 'delivery_app/home.html', context)

def about(request):
    company_info = CompanyInfo.objects.first()
    context = {
        'company_info': company_info,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/about.html', context)

def news(request):
    articles = Article.objects.order_by('-published_date')
    context = {
        'articles': articles,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/news.html', context)

def faq(request):
    faqs = FAQ.objects.order_by('-added_date')
    context = {
        'faqs': faqs,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/faq.html', context)

def contacts(request):
    employees = Employee.objects.all()
    context = {
        'employees': employees,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/contacts.html', context)

def privacy(request):
    context = {
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/privacy.html', context)

def vacancies(request):
    vacancies = Vacancy.objects.order_by('-created_date')
    context = {
        'vacancies': vacancies,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/vacancies.html', context)

@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Отзыв добавлен!")
            return redirect('delivery_app:reviews')
    else:
        form = ReviewForm()
    return render(request, 'delivery_app/add_review.html', {'form': form})

def reviews(request):
    reviews = Review.objects.order_by('-created_date')
    context = {
        'reviews': reviews,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/reviews.html', context)

def promocodes(request):
    active_promocodes = PromoCode.objects.filter(valid_to__gte=timezone.now())
    archived_promocodes = PromoCode.objects.filter(valid_to__lt=timezone.now())
    context = {
        'active_promocodes': active_promocodes,
        'archived_promocodes': archived_promocodes,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/promocodes.html', context)

def product_list(request):
    # Получаем все товары и типы товаров
    products = Product.objects.all()
    product_types = ProductType.objects.all()

    # Получаем параметры поиска и фильтрации
    search_query = request.GET.get('search', '').strip()
    type_filter = request.GET.get('type', '').strip()
    sort_by = request.GET.get('sort', 'name').strip()

    # Логируем параметры для отладки
    logger.debug(f"Search query: {search_query}, Type filter: {type_filter}, Sort by: {sort_by}")

    # Фильтрация товаров
    # Сначала применяем фильтр по типу, если он есть
    if type_filter:
        products = products.filter(product_type__name=type_filter)
        logger.debug(f"Filtered by type '{type_filter}': {products.count()} products")

    # Затем применяем поиск, если есть запрос
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        logger.debug(f"Filtered by search '{search_query}': {products.count()} products")

    # Сортировка
    if sort_by in ['name', 'price']:
        products = products.order_by(sort_by)
    else:
        products = products.order_by('name')  # Значение по умолчанию
    logger.debug(f"Final product count after sorting: {products.count()}")

    context = {
        'products': products,
        'product_types': product_types,
        'search_query': search_query,
        'type_filter': type_filter,
        'sort_by': sort_by,
    }
    return render(request, 'delivery_app/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'timezone': 'Europe/Minsk',
    }
    return render(request, 'delivery_app/product_detail.html', context)