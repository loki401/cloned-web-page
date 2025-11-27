from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),  # /products/
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    path('<int:product_id>/add-review/', views.add_review, name='add_review'),
    path('<int:product_id>/delete-review/', views.delete_review, name='delete_review'),
    path('<int:product_id>/rating-data/', views.get_product_rating, name='product_rating_data'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('search/', views.search_results, name='search_results'),
]