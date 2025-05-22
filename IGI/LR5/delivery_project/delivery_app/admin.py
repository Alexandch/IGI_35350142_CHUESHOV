from django.contrib import admin
from .models import FAQ, Article, CompanyInfo, Employee, Client, Manufacturer, ProductType, Product, Order, OrderItem, PromoCode, PickupPoint, Review, Vacancy

# Регистрация модели Employee
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'date_of_birth')
    search_fields = ('user__username', 'position')
    list_filter = ('position',)

# Регистрация модели Client
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__username', 'phone')
    list_filter = ('date_of_birth',)

# Регистрация модели ProductType
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Регистрация модели Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'unit_of_measurement', 'product_type')
    search_fields = ('name',)
    list_filter = ('product_type', 'unit_of_measurement')

# Встроенное редактирование OrderItem в Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Регистрация модели Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'employee', 'date_ordered', 'status', 'total_cost', 'pickup_point', 'delivery_cost', 'delivery_method')
    search_fields = ('client__user__username', 'employee__user__username')
    list_filter = ('status', 'date_ordered', 'pickup_point', 'delivery_method')
    inlines = [OrderItemInline]

    def total_cost(self, obj):
        return sum(item.price * item.quantity for item in obj.orderitem_set.all())

# Регистрация модели OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('product__name',)
    list_filter = ('order',)

# Регистрация модели PromoCode
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'valid_from', 'valid_to', 'active')
    search_fields = ('code',)
    list_filter = ('active', 'valid_from', 'valid_to')
    list_editable = ('discount', 'active')

# Регистрация модели PickupPoint
@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'working_hours')
    search_fields = ('name', 'address')
    list_filter = ('name',)

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)    

# Регистрация модели CompanyInfo
@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'history', 'requisites')
    search_fields = ('name', 'description')
    list_filter = ('name',)

# Регистрация модели Article
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'summary', 'published_date')
    search_fields = ('title', 'summary')
    list_filter = ('published_date',)
    list_editable = ('summary',)  # Встроенное редактирование

# Регистрация модели FAQ
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'added_date')
    search_fields = ('question', 'answer')
    list_filter = ('added_date',)
    list_editable = ('answer',)  # Встроенное редактирование

# Регистрация модели Vacancy
@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_date')
    search_fields = ('title', 'description')
    list_filter = ('created_date',)
    list_editable = ('description',)  # Встроенное редактирование

# Регистрация модели Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'text', 'created_date')
    search_fields = ('user__username', 'text')
    list_filter = ('rating', 'created_date')
    list_editable = ('rating', 'text')  # Встроенное редактирование