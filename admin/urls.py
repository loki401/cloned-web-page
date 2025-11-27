from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('products/', views.product_management, name='product_management'),
    path('orders/', views.order_management, name='order_management'),
    path('categories/', views.category_management, name='category_management'),
]
