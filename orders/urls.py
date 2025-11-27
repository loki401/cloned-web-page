from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.orders, name='orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('place/', views.place_order, name='place_order'),
    path('<int:order_id>/success/', views.order_success, name='order_success'),
    path('<int:order_id>/invoice/', views.download_invoice, name='download_invoice'),
    path('<int:order_id>/invoice-pdf/', views.download_pdf_invoice, name='download_pdf_invoice'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
]