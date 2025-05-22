from . import views
from django.urls import path, re_path
from .views import ProductListView, OrderDetailView, home_view

app_name = 'delivery_app'

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    re_path(r'^products/(?P<product_id>\d+)/$', views.product_detail, name='product_detail'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('create-order/', views.create_order, name='create_order'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/edit/', views.edit_order, name='edit_order'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile, name='profile'),
    path('employee-panel/', views.employee_panel, name='employee_panel'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('employee-products/', views.employee_products, name='employee_products'),
    #path('accounts/logout/', views.custom_logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('faq/', views.faq, name='faq'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('add-review/', views.add_review, name='add_review'),
    path('promocodes/', views.promocodes, name='promocodes'),
]