from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category, ProductReview
from orders.models import Order, OrderItem
from cart.models import Cart, CartItem
from users.models import UserProfile

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    # Get statistics for dashboard
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Top selling products
    top_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    # Monthly stats
    current_month = timezone.now().replace(day=1)
    monthly_orders = Order.objects.filter(created_at__gte=current_month).count()
    monthly_revenue = Order.objects.filter(
        created_at__gte=current_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'monthly_orders': monthly_orders,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def user_management(request):
    users = User.objects.select_related('userprofile').order_by('-date_joined')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        user = get_object_or_404(User, id=user_id)
        
        if action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f'User {user.username} has been activated.')
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'User {user.username} has been deactivated.')
        elif action == 'delete':
            username = user.username
            user.delete()
            messages.success(request, f'User {username} has been deleted.')
            
        return redirect('custom_admin:user_management')
    
    context = {'users': users}
    return render(request, 'admin/user_management.html', context)

@login_required
@user_passes_test(is_superuser)
def product_management(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_product':
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            category_id = request.POST.get('category')
            stock_quantity = request.POST.get('stock_quantity')
            image = request.FILES.get('image')
            
            category = get_object_or_404(Category, id=category_id)
            
            Product.objects.create(
                name=name,
                slug=name.lower().replace(' ', '-').replace('_', '-'),
                description=description,
                price=price,
                category=category,
                stock=stock_quantity,
                image=image
            )
            messages.success(request, 'Product added successfully.')
            
        elif action == 'edit_product':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            
            product.name = request.POST.get('name')
            product.description = request.POST.get('description')
            product.short_description = request.POST.get('short_description', '')
            product.price = request.POST.get('price')
            product.mrp = request.POST.get('mrp') or None
            product.discount_percentage = request.POST.get('discount_percentage', 0)
            product.stock = request.POST.get('stock_quantity')
            product.is_active = request.POST.get('is_active') == 'on'
            product.featured = request.POST.get('featured') == 'on'
            
            category_id = request.POST.get('category')
            product.category = get_object_or_404(Category, id=category_id)
            
            # Handle image upload
            if request.FILES.get('image'):
                product.image = request.FILES.get('image')
            
            # Update slug if name changed
            product.slug = product.name.lower().replace(' ', '-').replace('_', '-')
            product.save()
            
            messages.success(request, f'Product "{product.name}" has been updated successfully.')
            
        elif action == 'delete_product':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product_name = product.name
            product.delete()
            messages.success(request, f'Product "{product_name}" has been deleted.')
            
        return redirect('custom_admin:product_management')
    
    # Calculate statistics
    available_products = products.filter(is_active=True).count()
    low_stock_products = products.filter(stock__lte=10, stock__gt=0).count()
    out_of_stock_products = products.filter(stock=0).count()
    
    context = {
        'products': products,
        'categories': categories,
        'available_products': available_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
    }
    return render(request, 'admin/product_management.html', context)

@login_required
@user_passes_test(is_superuser)
def order_management(request):
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')
    
    # Calculate order statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    processing_orders = orders.filter(status='processing').count()
    shipped_orders = orders.filter(status='shipped').count()
    delivered_orders = orders.filter(status='delivered').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        
        messages.success(request, f'Order #{order.id} status updated to {new_status}.')
        return redirect('custom_admin:order_management')
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
    }
    return render(request, 'admin/order_management.html', context)

@login_required
@user_passes_test(is_superuser)
def category_management(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')
    
    # Calculate category statistics
    total_categories = categories.count()
    categories_with_products = categories.filter(product_count__gt=0).count()
    empty_categories = categories.filter(product_count=0).count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_category':
            name = request.POST.get('name')
            slug = request.POST.get('slug') or name.lower().replace(' ', '-').replace('_', '-')
            
            Category.objects.create(
                name=name,
                slug=slug
            )
            messages.success(request, 'Category added successfully.')
            
        elif action == 'edit_category':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            
            category.name = request.POST.get('name')
            category.slug = request.POST.get('slug') or category.name.lower().replace(' ', '-').replace('_', '-')
            
            # Handle image upload
            if request.FILES.get('image'):
                category.image = request.FILES.get('image')
            
            category.save()
            messages.success(request, f'Category "{category.name}" has been updated successfully.')
            
        elif action == 'delete_category':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category_name = category.name
            category.delete()
            messages.success(request, f'Category "{category_name}" has been deleted.')
            
        return redirect('custom_admin:category_management')
    
    context = {
        'categories': categories,
        'total_categories': total_categories,
        'categories_with_products': categories_with_products,
        'empty_categories': empty_categories,
    }
    return render(request, 'admin/category_management.html', context)
