"""
URL configuration for flipkart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import home, customer_care
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Home page
    path('users/', include('users.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('admin-panel/', include('admin.urls')),
    path('products/', include('products.urls')),
    path('customer-care/', customer_care, name='customer_care'),
    path('become-seller/', views.become_seller, name='become_seller'),
    path('advertise/', views.advertise, name='advertise'),
    path('gift-cards/', views.gift_cards, name='gift_cards'),
    path('gift-cards/redeem/', views.redeem_gift_card, name='redeem_gift_card'),
    path('gift-cards/balance/', views.check_gift_card_balance, name='check_gift_card_balance'),
    path('help-center/', views.help_center, name='help_center'),
    # path('contact/', include('contact.urls')),  # Removed because contact app does not exist
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
