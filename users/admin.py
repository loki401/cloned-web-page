from django.contrib import admin
from .models import UserProfile, Address, PasswordResetOTP, Wishlist, Notification, GiftCard

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'state', 'is_default']
    list_filter = ['is_default', 'state', 'city']
    search_fields = ['user__username', 'full_name', 'city']

@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_filter = ['notification_type', 'is_read', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"

@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ['card_number', 'recipient_name', 'amount', 'remaining_balance', 'status', 'created_at', 'is_delivered']
    search_fields = ['card_number', 'recipient_name', 'recipient_email', 'purchaser_email']
    list_filter = ['status', 'is_delivered', 'is_scheduled', 'created_at']
    readonly_fields = ['card_number', 'security_code', 'created_at', 'delivered_at', 'redeemed_at']
    actions = ['mark_as_delivered', 'send_gift_card_email']
    
    fieldsets = (
        ('Gift Card Details', {
            'fields': ('card_number', 'security_code', 'amount', 'remaining_balance', 'status')
        }),
        ('Recipient Information', {
            'fields': ('recipient_name', 'recipient_email', 'personal_message')
        }),
        ('Purchaser Information', {
            'fields': ('purchaser', 'purchaser_email')
        }),
        ('Delivery & Status', {
            'fields': ('delivery_date', 'is_scheduled', 'is_delivered', 'delivered_at')
        }),
        ('Redemption Details', {
            'fields': ('redeemed_at', 'redeemed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at')
        }),
    )
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_delivered=True, delivered_at=timezone.now())
        self.message_user(request, f"{updated} gift cards marked as delivered.")
    mark_as_delivered.short_description = "Mark selected gift cards as delivered"
    
    def send_gift_card_email(self, request, queryset):
        from .views import send_gift_card_email
        count = 0
        for gift_card in queryset:
            if send_gift_card_email(gift_card):
                count += 1
        self.message_user(request, f"Gift card emails sent for {count} cards.")
    send_gift_card_email.short_description = "Send gift card emails"
