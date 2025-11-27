from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import random
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Addresses'
    
    def __str__(self):
        return f"{self.full_name} - {self.city}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        verbose_name_plural = 'Wishlist Items'
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_placed', 'Order Placed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('wishlist_item_sale', 'Wishlist Item on Sale'),
        ('product_back_in_stock', 'Product Back in Stock'),
        ('account_update', 'Account Update'),
        ('welcome', 'Welcome'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields for linking to specific objects
    order_id = models.IntegerField(blank=True, null=True)
    product_id = models.IntegerField(blank=True, null=True)
    
    # Optional action URL
    action_url = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def get_icon_class(self):
        """Return appropriate icon class based on notification type"""
        icon_map = {
            'order_placed': 'fas fa-shopping-cart text-success',
            'order_shipped': 'fas fa-truck text-info',
            'order_delivered': 'fas fa-check-circle text-success',
            'order_cancelled': 'fas fa-times-circle text-danger',
            'wishlist_item_sale': 'fas fa-heart text-danger',
            'product_back_in_stock': 'fas fa-box text-primary',
            'account_update': 'fas fa-user text-info',
            'welcome': 'fas fa-star text-warning',
            'general': 'fas fa-bell text-secondary',
        }
        return icon_map.get(self.notification_type, 'fas fa-bell text-secondary')

class GiftCard(models.Model):
    GIFT_CARD_STATUS = [
        ('active', 'Active'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
    ]
    
    # Gift card details
    card_number = models.CharField(max_length=16, unique=True)
    security_code = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Recipient information
    recipient_name = models.CharField(max_length=100)
    recipient_email = models.EmailField()
    personal_message = models.TextField(blank=True)
    
    # Purchaser information
    purchaser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_gift_cards', null=True, blank=True)
    purchaser_email = models.EmailField()
    
    # Status and dates
    status = models.CharField(max_length=20, choices=GIFT_CARD_STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True, blank=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='redeemed_gift_cards')
    
    # Delivery settings
    delivery_date = models.DateTimeField(null=True, blank=True)
    is_scheduled = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Gift Card'
        verbose_name_plural = 'Gift Cards'
    
    def __str__(self):
        return f"Gift Card {self.card_number} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = self.generate_card_number()
        if not self.security_code:
            self.security_code = self.generate_security_code()
        if not self.remaining_balance:
            self.remaining_balance = self.amount
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=365)  # 1 year validity
        super().save(*args, **kwargs)
    
    def generate_card_number(self):
        """Generate a unique 16-digit gift card number"""
        import random
        while True:
            card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            if not GiftCard.objects.filter(card_number=card_number).exists():
                return card_number
    
    def generate_security_code(self):
        """Generate a 6-digit security code"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    def is_valid(self):
        """Check if gift card is valid for use"""
        return (
            self.status == 'active' and 
            self.remaining_balance > 0 and 
            timezone.now() <= self.expires_at
        )
    
    def redeem(self, amount, user=None):
        """Redeem specified amount from gift card"""
        if not self.is_valid():
            raise ValueError("Gift card is not valid for redemption")
        
        if amount > self.remaining_balance:
            raise ValueError("Insufficient balance on gift card")
        
        self.remaining_balance -= amount
        if self.remaining_balance == 0:
            self.status = 'redeemed'
            self.redeemed_at = timezone.now()
            self.redeemed_by = user
        
        self.save()
        return self.remaining_balance
    
    def get_formatted_card_number(self):
        """Return formatted card number (XXXX-XXXX-XXXX-XXXX)"""
        return '-'.join([self.card_number[i:i+4] for i in range(0, 16, 4)])
    
    def get_masked_card_number(self):
        """Return masked card number for security (XXXX-XXXX-XXXX-1234)"""
        return f"XXXX-XXXX-XXXX-{self.card_number[-4:]}"
