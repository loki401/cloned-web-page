from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category, ProductReview

def home(request):
    categories = Category.objects.all()[:8]  # Get first 8 categories
    featured_products = Product.objects.filter(featured=True, is_active=True)[:8]
    
    # If no featured products, get latest products
    if not featured_products:
        featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get user's wishlist if authenticated
    user_wishlist = []
    if request.user.is_authenticated:
        from users.models import Wishlist
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(request, 'products/home.html', {
        'categories': categories, 
        'products': featured_products,
        'user_wishlist': user_wishlist
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get product reviews and ratings
    reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = ProductReview.objects.get(product=product, user=request.user)
        except ProductReview.DoesNotExist:
            pass
    
    # Get user's wishlist if authenticated
    user_wishlist = []
    if request.user.is_authenticated:
        from users.models import Wishlist
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'user_wishlist': user_wishlist,
        'reviews': reviews,
        'user_review': user_review
    })

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True).order_by('-created_at')
    
    # Get user's wishlist if authenticated
    user_wishlist = []
    if request.user.is_authenticated:
        from users.models import Wishlist
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(request, 'products/category.html', {
        'category': category, 
        'products': products,
        'user_wishlist': user_wishlist
    })

def search_results(request):
    query = request.GET.get('q', '')
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(short_description__icontains=query),
            is_active=True
        ).order_by('-created_at')
    
    # Get user's wishlist if authenticated
    user_wishlist = []
    if request.user.is_authenticated:
        from users.models import Wishlist
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(request, 'products/search_results.html', {
        'query': query, 
        'products': products,
        'user_wishlist': user_wishlist
    })

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    # Get user's wishlist if authenticated
    user_wishlist = []
    if request.user.is_authenticated:
        from users.models import Wishlist
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    # Apply filters
    category_filter = request.GET.getlist('category')
    if category_filter:
        products = products.filter(category__id__in=category_filter)
    
    min_price = request.GET.get('min_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(price__lte=max_price)
    
    rating_filter = request.GET.get('rating')
    if rating_filter:
        # Filter products with average rating >= selected rating
        from django.db.models import Avg
        products = products.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=rating_filter)
    
    in_stock = request.GET.get('in_stock')
    if in_stock:
        products = products.filter(stock__gt=0)
    
    # Apply sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        from django.db.models import Avg
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')  # default sorting
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'user_wishlist': user_wishlist
    })

def customer_care(request):
    return render(request, 'customer_care.html')

@login_required
def product_reviews(request, product_id):
    """Display all reviews for a product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
    
    # Get user's review if exists
    user_review = None
    try:
        user_review = ProductReview.objects.get(product=product, user=request.user)
    except ProductReview.DoesNotExist:
        pass
    
    # Calculate rating distribution
    rating_counts = {i: 0 for i in range(1, 6)}
    for review in reviews:
        rating_counts[review.rating] += 1
    
    # Calculate percentages for rating bars
    total_reviews_count = reviews.count()
    rating_percentages = {}
    for i in range(1, 6):
        if total_reviews_count > 0:
            rating_percentages[i] = (rating_counts[i] * 100) // total_reviews_count
        else:
            rating_percentages[i] = 0
    
    return render(request, 'products/product_reviews.html', {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'rating_counts': rating_counts,
        'total_reviews': reviews.count()
    })

@login_required
def add_review(request, product_id):
    """Add or update a product review"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if not rating or int(rating) not in range(1, 6):
            messages.error(request, 'Please select a valid rating (1-5 stars).')
            return redirect('products:product_detail', product_id=product_id)
        
        # Create or update review
        review, created = ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': int(rating),
                'comment': comment
            }
        )
        
        if created:
            messages.success(request, 'Thank you for your review!')
            # Create notification for review submission
            try:
                from users.views import create_notification
                create_notification(
                    user=request.user,
                    title="Review Submitted Successfully",
                    message=f"Your review for {product.name} has been submitted. Thank you for your feedback!",
                    notification_type='general',
                    product_id=product.id,
                    action_url=f'/products/{product.id}/'
                )
            except ImportError:
                pass
        else:
            messages.success(request, 'Your review has been updated!')
        
        return redirect('products:product_detail', product_id=product_id)
    
    return redirect('products:product_detail', product_id=product_id)

@login_required
def delete_review(request, product_id):
    """Delete user's review for a product"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        try:
            review = ProductReview.objects.get(product=product, user=request.user)
            review.delete()
            messages.success(request, 'Your review has been deleted.')
        except ProductReview.DoesNotExist:
            messages.error(request, 'Review not found.')
    
    return redirect('products:product_detail', product_id=product_id)

def get_product_rating(request, product_id):
    """AJAX endpoint to get product rating data"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    return JsonResponse({
        'average_rating': product.average_rating,
        'review_count': product.review_count,
        'rating_distribution': {
            str(i): ProductReview.objects.filter(product=product, rating=i).count()
            for i in range(1, 6)
        }
    })
