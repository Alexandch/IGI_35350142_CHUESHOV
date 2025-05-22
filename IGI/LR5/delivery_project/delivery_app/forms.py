from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Client, Order, OrderItem, Product, Review
from django.utils import timezone
import re

# Кастомная форма регистрации пользователя
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

# Форма для клиента
class ClientForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=True)
    class Meta:
        model = Client
        fields = ['phone', 'address', 'date_of_birth', 'email']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r'^\+375\s\(29\)\s\d{3}-\d{2}-\d{2}$', phone):
            raise forms.ValidationError("Формат номера: +375 (29) XXX-XX-XX")
        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        today = timezone.now().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise forms.ValidationError("Возраст должен быть 18+.")
        return dob
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Получаем пользователя
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email  # Устанавливаем начальное значение

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']  # Обновляем email пользователя
            if commit:
                self.user.save()
        if commit:
            instance.save()
        return instance

# Форма для заказа
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'employee', 'status', 'date_delivered']

# Форма для элемента заказа
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']