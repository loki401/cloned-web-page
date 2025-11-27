from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Notification
from users.views import create_notification


class Command(BaseCommand):
    help = 'Create sample notifications for testing'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to create notifications for')

    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
                return
        else:
            # Get first user or create one
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return

        # Create sample notifications
        notifications_data = [
            {
                'title': 'Welcome to Flipkart Clone!',
                'message': 'Thank you for joining us! Explore our amazing collection of products and enjoy great deals.',
                'notification_type': 'welcome',
                'action_url': '/products/'
            },
            {
                'title': 'Order Placed Successfully',
                'message': 'Your order #12345 has been placed successfully. We will notify you once it ships.',
                'notification_type': 'order_placed',
                'order_id': 12345,
                'action_url': '/users/orders/'
            },
            {
                'title': 'Your Order is Out for Delivery',
                'message': 'Great news! Your order #12345 is out for delivery and will reach you soon.',
                'notification_type': 'order_shipped',
                'order_id': 12345,
                'action_url': '/users/orders/'
            },
            {
                'title': 'Wishlist Item on Sale!',
                'message': 'The iPhone 13 in your wishlist is now available at a special discount. Don\'t miss out!',
                'notification_type': 'wishlist_item_sale',
                'product_id': 1,
                'action_url': '/products/1/'
            },
            {
                'title': 'Product Back in Stock',
                'message': 'Good news! The Samsung Galaxy S21 you were looking for is back in stock.',
                'notification_type': 'product_back_in_stock',
                'product_id': 2,
                'action_url': '/products/2/'
            },
            {
                'title': 'Profile Updated',
                'message': 'Your profile information has been updated successfully.',
                'notification_type': 'account_update',
                'action_url': '/users/profile/'
            },
            {
                'title': 'Special Offer Just for You',
                'message': 'Get 20% off on electronics! Use code SAVE20 at checkout. Valid till tomorrow.',
                'notification_type': 'general',
                'action_url': '/products/'
            }
        ]

        created_count = 0
        for notification_data in notifications_data:
            notification = create_notification(
                user=user,
                **notification_data
            )
            created_count += 1
            self.stdout.write(f'Created notification: {notification.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample notifications for user "{user.username}"')
        )
