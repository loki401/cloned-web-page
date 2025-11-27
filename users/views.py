from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .forms import RegistrationForm, LoginForm, ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm, UserEditForm, UserProfileEditForm, AddressForm
from .models import PasswordResetOTP, UserProfile, Address, Wishlist, Notification

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create welcome notification
            create_notification(
                user=user,
                title="Welcome to Flipkart Clone!",
                message=f"Hi {user.first_name or user.username}! Welcome to our platform. Start exploring amazing products and deals.",
                notification_type='welcome',
                action_url='/products/'
            )
            
            login(request, user)
            return redirect('users:profile')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Login attempt - Username: {username}, Password: {password}")  # Debug
        
        # Try to authenticate with username first
        user = authenticate(request, username=username, password=password)
        print(f"Username auth result: {user}")  # Debug
        
        # If that fails, try with email
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                print(f"Found user by email: {user_obj.username}")  # Debug
                user = authenticate(request, username=user_obj.username, password=password)
                print(f"Email auth result: {user}")  # Debug
            except User.DoesNotExist:
                print("No user found with that email")  # Debug
                pass
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect superusers to admin dashboard
                if user.is_superuser:
                    return redirect('custom_admin:dashboard')
                
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account is inactive.')
        else:
            # Check if user exists at all
            user_exists = User.objects.filter(username=username).exists() or User.objects.filter(email=username).exists()
            if user_exists:
                messages.error(request, 'Incorrect password. Please try again.')
            else:
                messages.error(request, 'No account found with this username/email.')
    
    return render(request, 'users/login.html')

@login_required
def profile(request):
    user = request.user
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user addresses
    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    
    # Get user orders (import Order model from orders app)
    try:
        from orders.models import Order
        orders = Order.objects.filter(user=user).order_by('-created_at')[:5]  # Show recent 5 orders
    except ImportError:
        orders = []
    
    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'addresses': addresses
    }
    return render(request, 'users/profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('users:login')

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Delete any existing OTPs for this user
            PasswordResetOTP.objects.filter(user=user, is_used=False).delete()
            
            # Create new OTP
            otp_obj = PasswordResetOTP.objects.create(user=user)
            
            # Send OTP email
            try:
                send_mail(
                    subject='Password Reset OTP - Flipkart Clone',
                    message=f'Your OTP for password reset is: {otp_obj.otp}\n\nThis OTP will expire in 10 minutes.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f'OTP sent to {email}. Please check your email.')
                request.session['reset_user_id'] = user.id
                return redirect('users:verify_otp')
            except Exception as e:
                messages.error(request, 'Failed to send OTP. Please try again.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'users/forgot_password.html', {'form': form})

def verify_otp(request):
    if 'reset_user_id' not in request.session:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('users:forgot_password')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            user_id = request.session['reset_user_id']
            
            try:
                otp_obj = PasswordResetOTP.objects.get(
                    user_id=user_id,
                    otp=otp,
                    is_used=False
                )
                
                if otp_obj.is_valid():
                    request.session['verified_otp_id'] = otp_obj.id
                    return redirect('users:reset_password')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'users/verify_otp.html', {'form': form})

def reset_password(request):
    if 'verified_otp_id' not in request.session:
        messages.error(request, 'Invalid session. Please complete OTP verification first.')
        return redirect('users:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            otp_id = request.session['verified_otp_id']
            
            try:
                otp_obj = PasswordResetOTP.objects.get(id=otp_id, is_used=False)
                user = otp_obj.user
                
                # Update password
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                
                # Mark OTP as used
                otp_obj.is_used = True
                otp_obj.save()
                
                # Clear session
                del request.session['reset_user_id']
                del request.session['verified_otp_id']
                
                messages.success(request, 'Password reset successfully. You can now login with your new password.')
                return redirect('users:login')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid session. Please start the password reset process again.')
                return redirect('users:forgot_password')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'users/reset_password.html', {'form': form})

def resend_otp(request):
    if 'reset_user_id' not in request.session:
        messages.error(request, 'Invalid session.')
        return redirect('users:forgot_password')
    
    user_id = request.session['reset_user_id']
    user = User.objects.get(id=user_id)
    
    # Delete existing OTPs
    PasswordResetOTP.objects.filter(user=user, is_used=False).delete()
    
    # Create new OTP
    otp_obj = PasswordResetOTP.objects.create(user=user)
    
    # Send OTP email
    try:
        send_mail(
            subject='Password Reset OTP - Flipkart Clone',
            message=f'Your new OTP for password reset is: {otp_obj.otp}\n\nThis OTP will expire in 10 minutes.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(request, 'New OTP sent to your email.')
    except Exception as e:
        messages.error(request, 'Failed to send OTP. Please try again.')
    
    return redirect('users:verify_otp')

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user, user=user)
        profile_form = UserProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        user_form = UserEditForm(instance=user, user=user)
        profile_form = UserProfileEditForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'profile': profile
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def manage_addresses(request):
    user = request.user
    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    
    context = {
        'addresses': addresses,
        'user': user
    }
    return render(request, 'users/manage_addresses.html', context)

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, remove default from other addresses
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('users:manage_addresses')
    else:
        form = AddressForm()
    
    context = {
        'form': form,
        'title': 'Add New Address'
    }
    return render(request, 'users/address_form.html', context)

@login_required
def edit_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)
            
            # If this is set as default, remove default from other addresses
            if updated_address.is_default:
                Address.objects.filter(user=request.user, is_default=True).exclude(id=address_id).update(is_default=False)
            
            updated_address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('users:manage_addresses')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
        'title': 'Edit Address'
    }
    return render(request, 'users/address_form.html', context)

@login_required
def delete_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('users:manage_addresses')

@login_required
def my_orders(request):
    user = request.user
    try:
        from orders.models import Order
        orders = Order.objects.filter(user=user).order_by('-created_at')
    except ImportError:
        orders = []
    
    context = {
        'orders': orders,
        'user': user
    }
    return render(request, 'users/my_orders.html', context)

@login_required
def my_wishlist(request):
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user).select_related('product').order_by('-created_at')
    
    context = {
        'wishlist_items': wishlist_items,
        'user': user
    }
    return render(request, 'users/my_wishlist.html', context)

@login_required
def payment_methods(request):
    user = request.user
    # Placeholder for payment methods
    payment_methods = []
    
    context = {
        'payment_methods': payment_methods,
        'user': user
    }
    return render(request, 'users/payment_methods.html', context)

@login_required
def notifications(request):
    user = request.user
    notifications_list = Notification.objects.filter(user=user).order_by('-created_at')
    unread_count = notifications_list.filter(is_read=False).count()
    
    # Mark notifications as read when viewing the page
    if request.GET.get('mark_read') == 'true':
        notifications_list.filter(is_read=False).update(is_read=True)
        return redirect('users:notifications')
    
    context = {
        'notifications': notifications_list,
        'unread_count': unread_count,
        'user': user
    }
    return render(request, 'users/notifications.html', context)

@login_required
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        try:
            from products.models import Product
            product = Product.objects.get(id=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
            
            if created:
                messages.success(request, f'{product.name} added to wishlist!')
            else:
                messages.info(request, f'{product.name} is already in your wishlist!')
                
        except Product.DoesNotExist:
            messages.error(request, 'Product not found!')
        except Exception as e:
            messages.error(request, 'Error adding to wishlist!')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_wishlist(request, product_id):
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product_id=product_id)
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        messages.success(request, f'{product_name} removed from wishlist!')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Item not found in wishlist!')
    except Exception as e:
        messages.error(request, 'Error removing from wishlist!')
    
    return redirect(request.META.get('HTTP_REFERER', 'users:my_wishlist'))

@login_required
def toggle_wishlist(request, product_id):
    """AJAX endpoint for toggling wishlist items"""
    if request.method == 'POST':
        try:
            from products.models import Product
            product = Product.objects.get(id=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
            
            if not created:
                wishlist_item.delete()
                is_in_wishlist = False
                message = f'{product.name} removed from wishlist!'
            else:
                is_in_wishlist = True
                message = f'{product.name} added to wishlist!'
                
                # Create notification for adding to wishlist
                create_notification(
                    user=request.user,
                    title="Item Added to Wishlist",
                    message=f"You've added {product.name} to your wishlist. We'll notify you about price drops and offers!",
                    notification_type='wishlist_item_sale',
                    product_id=product.id,
                    action_url=f'/products/{product.id}/'
                )
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'is_in_wishlist': is_in_wishlist,
                'message': message
            })
            
        except Product.DoesNotExist:
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'message': 'Product not found!'
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'message': 'Error updating wishlist!'
            })
    
    from django.http import JsonResponse
    return JsonResponse({'success': False, 'message': 'Invalid request method!'})

@login_required
def get_notifications_count(request):
    """AJAX endpoint to get unread notifications count"""
    from django.http import JsonResponse
    
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def mark_notification_read(request, notification_id):
    """AJAX endpoint to mark a specific notification as read"""
    from django.http import JsonResponse
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True, 'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Notification not found'})

@login_required
def mark_all_notifications_read(request):
    """AJAX endpoint to mark all notifications as read"""
    from django.http import JsonResponse
    
    if request.method == 'POST':
        updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True, 'message': f'{updated_count} notifications marked as read'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def create_notification(user, title, message, notification_type='general', order_id=None, product_id=None, action_url=None):
    """Helper function to create notifications"""
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        order_id=order_id,
        product_id=product_id,
        action_url=action_url
    )
    return notification
