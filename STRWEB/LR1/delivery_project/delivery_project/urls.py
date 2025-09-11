from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('delivery_app.urls')), 
    #path('accounts/', include('django.contrib.auth.urls')),  
    path('accounts/login/', LoginView.as_view(template_name='delivery_app/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
]