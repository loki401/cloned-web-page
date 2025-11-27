from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from products.models import Product

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'grand_total': cart.total_price
    })

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity + 1 > product.stock:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock'
                })
            # Add message for non-AJAX requests if needed, or handle in template
        else:
            cart_item.quantity += 1
            cart_item.save()
    elif product.stock < 1:
        # Should not happen if button is disabled, but good for safety
        cart_item.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Product is out of stock'
            })
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_items,
            'message': f'{product.name} added to cart'
        })
    
    return redirect('cart:cart')

@login_required
@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        if quantity > cart_item.product.stock:
            # If requested quantity is more than stock, set to max stock
            cart_item.quantity = cart_item.product.stock
            # You might want to add a message here
        else:
            cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart:cart')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Item removed from cart'})
        
        return redirect('cart:cart')
    except CartItem.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Item not found in cart'})
        
        return redirect('cart:cart')
