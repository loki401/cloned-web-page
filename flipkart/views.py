from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import json
from datetime import datetime

def contact(request):
    return render(request, 'contact/contact.html')

def become_seller(request):
    return render(request, 'pages/become_seller.html')

def advertise(request):
    return render(request, 'pages/advertise.html')

def gift_cards(request):
    if request.method == 'POST':
        return handle_gift_card_purchase(request)
    return render(request, 'pages/gift_cards.html')

def help_center(request):
    return render(request, 'pages/help_center.html')

@csrf_exempt
def handle_gift_card_purchase(request):
    """Handle gift card purchase and email delivery"""
    try:
        # Get form data
        recipient_name = request.POST.get('recipient_name')
        recipient_email = request.POST.get('recipient_email')
        amount = request.POST.get('amount')
        custom_amount = request.POST.get('custom_amount')
        personal_message = request.POST.get('personal_message', '')
        delivery_type = request.POST.get('delivery')
        delivery_date = request.POST.get('delivery_date')
        
        # Validate required fields
        if not all([recipient_name, recipient_email]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'pages/gift_cards.html')
        
        # Determine final amount
        final_amount = custom_amount if custom_amount else amount
        if not final_amount:
            messages.error(request, 'Please select or enter a gift card amount.')
            return render(request, 'pages/gift_cards.html')
        
        try:
            final_amount = float(final_amount)
            if final_amount < 100 or final_amount > 50000:
                messages.error(request, 'Gift card amount must be between ₹100 and ₹50,000.')
                return render(request, 'pages/gift_cards.html')
        except ValueError:
            messages.error(request, 'Invalid amount entered.')
            return render(request, 'pages/gift_cards.html')
        
        # Create gift card
        from users.models import GiftCard
        
        gift_card = GiftCard.objects.create(
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            personal_message=personal_message,
            amount=final_amount,
            purchaser=request.user if request.user.is_authenticated else None,
            purchaser_email=request.user.email if request.user.is_authenticated else 'guest@flipkart.com',
            is_scheduled=(delivery_type == 'scheduled'),
            delivery_date=datetime.strptime(delivery_date, '%Y-%m-%d') if delivery_date else timezone.now()
        )
        
        # Send email immediately or schedule for later
        if delivery_type == 'immediate' or not delivery_date:
            success = send_gift_card_email(gift_card)
            if success:
                gift_card.is_delivered = True
                gift_card.delivered_at = timezone.now()
                gift_card.save()
                
                messages.success(request, f'Gift card sent successfully to {recipient_email}!')
                
                # Create notification for purchaser if logged in
                if request.user.is_authenticated:
                    from users.views import create_notification
                    create_notification(
                        user=request.user,
                        title="Gift Card Purchased Successfully",
                        message=f"Your gift card of ₹{final_amount} has been sent to {recipient_name} ({recipient_email})",
                        notification_type='general',
                        action_url='/gift-cards/'
                    )
            else:
                messages.error(request, 'Failed to send gift card email. Please try again.')
        else:
            messages.success(request, f'Gift card scheduled for delivery on {delivery_date}!')
        
        return redirect('gift_cards')
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'pages/gift_cards.html')

def send_gift_card_email(gift_card):
    """Send gift card email to recipient"""
    try:
        subject = f'🎁 You\'ve received a Flipkart Gift Card from {gift_card.purchaser.get_full_name() if gift_card.purchaser else "Someone Special"}!'
        
        # Render email template
        html_content = render_to_string('emails/gift_card_email.html', {
            'gift_card': gift_card,
            'recipient_name': gift_card.recipient_name,
            'sender_name': gift_card.purchaser.get_full_name() if gift_card.purchaser else 'A Friend',
            'personal_message': gift_card.personal_message,
            'card_number': gift_card.get_formatted_card_number(),
            'security_code': gift_card.security_code,
            'amount': gift_card.amount,
            'expires_at': gift_card.expires_at,
        })
        
        # Send email
        send_mail(
            subject=subject,
            message=f'You have received a Flipkart Gift Card! Card Number: {gift_card.get_formatted_card_number()}, Security Code: {gift_card.security_code}, Amount: ₹{gift_card.amount}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[gift_card.recipient_email],
            html_message=html_content,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending gift card email: {e}")
        return False

@csrf_exempt
def redeem_gift_card(request):
    """Handle gift card redemption"""
    if request.method == 'POST':
        try:
            card_number = request.POST.get('card_number', '').replace('-', '')
            security_code = request.POST.get('security_code')
            
            if not all([card_number, security_code]):
                return JsonResponse({'success': False, 'message': 'Please enter both card number and security code.'})
            
            from users.models import GiftCard
            
            try:
                gift_card = GiftCard.objects.get(card_number=card_number, security_code=security_code)
                
                if not gift_card.is_valid():
                    return JsonResponse({'success': False, 'message': 'This gift card is expired or already fully redeemed.'})
                
                # Add to user's wallet/account (simplified - just show balance)
                return JsonResponse({
                    'success': True, 
                    'message': f'Gift card is valid! Balance: ₹{gift_card.remaining_balance}',
                    'balance': float(gift_card.remaining_balance),
                    'expires_at': gift_card.expires_at.strftime('%B %d, %Y')
                })
                
            except GiftCard.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid gift card number or security code.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt 
def check_gift_card_balance(request):
    """Check gift card balance"""
    if request.method == 'POST':
        try:
            card_number = request.POST.get('card_number', '').replace('-', '')
            
            if not card_number:
                return JsonResponse({'success': False, 'message': 'Please enter a card number.'})
            
            from users.models import GiftCard
            
            try:
                gift_card = GiftCard.objects.get(card_number=card_number)
                
                return JsonResponse({
                    'success': True,
                    'balance': float(gift_card.remaining_balance),
                    'status': gift_card.status,
                    'expires_at': gift_card.expires_at.strftime('%B %d, %Y'),
                    'is_valid': gift_card.is_valid()
                })
                
            except GiftCard.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Gift card not found.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})