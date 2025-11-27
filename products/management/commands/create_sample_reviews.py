from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Product, ProductReview
import random


class Command(BaseCommand):
    help = 'Create sample product reviews'

    def handle(self, *args, **options):
        # Sample review data
        sample_reviews = [
            {
                'rating': 5,
                'comment': 'Excellent product! Exceeded my expectations. Fast delivery and great quality.'
            },
            {
                'rating': 4,
                'comment': 'Very good product. Worth the money. Minor packaging issues but overall satisfied.'
            },
            {
                'rating': 5,
                'comment': 'Amazing quality and performance. Highly recommended to everyone!'
            },
            {
                'rating': 3,
                'comment': 'Average product. Does the job but nothing exceptional. Could be better for the price.'
            },
            {
                'rating': 4,
                'comment': 'Good value for money. Works as expected. Delivery was quick.'
            },
            {
                'rating': 5,
                'comment': 'Outstanding! This is exactly what I was looking for. Perfect in every way.'
            },
            {
                'rating': 2,
                'comment': 'Not satisfied with the quality. Expected better based on the description.'
            },
            {
                'rating': 4,
                'comment': 'Pretty good product. Some minor issues but overall happy with the purchase.'
            },
            {
                'rating': 5,
                'comment': 'Fantastic! Great build quality and excellent customer service.'
            },
            {
                'rating': 3,
                'comment': 'Okay product. It works but there are better alternatives available.'
            }
        ]

        # Sample user names for creating users if they don't exist
        sample_users = [
            {'username': 'amit_sharma', 'first_name': 'Amit', 'last_name': 'Sharma', 'email': 'amit@example.com'},
            {'username': 'priya_singh', 'first_name': 'Priya', 'last_name': 'Singh', 'email': 'priya@example.com'},
            {'username': 'rahul_kumar', 'first_name': 'Rahul', 'last_name': 'Kumar', 'email': 'rahul@example.com'},
            {'username': 'sneha_patel', 'first_name': 'Sneha', 'last_name': 'Patel', 'email': 'sneha@example.com'},
            {'username': 'vikash_gupta', 'first_name': 'Vikash', 'last_name': 'Gupta', 'email': 'vikash@example.com'},
            {'username': 'anita_verma', 'first_name': 'Anita', 'last_name': 'Verma', 'email': 'anita@example.com'},
            {'username': 'rajesh_jain', 'first_name': 'Rajesh', 'last_name': 'Jain', 'email': 'rajesh@example.com'},
            {'username': 'kavita_shah', 'first_name': 'Kavita', 'last_name': 'Shah', 'email': 'kavita@example.com'},
        ]

        # Create sample users if they don't exist
        users = []
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email']
                }
            )
            users.append(user)
            if created:
                self.stdout.write(f'Created user: {user.username}')

        # Get all products
        products = Product.objects.filter(is_active=True)
        
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Please create products first.'))
            return

        created_count = 0
        
        # Create reviews for each product
        for product in products:
            # Random number of reviews per product (2-6)
            num_reviews = random.randint(2, 6)
            selected_users = random.sample(users, min(num_reviews, len(users)))
            
            for user in selected_users:
                # Check if review already exists
                if not ProductReview.objects.filter(product=product, user=user).exists():
                    review_data = random.choice(sample_reviews)
                    
                    ProductReview.objects.create(
                        product=product,
                        user=user,
                        rating=review_data['rating'],
                        comment=review_data['comment']
                    )
                    created_count += 1
                    self.stdout.write(f'Created review for {product.name} by {user.get_full_name()}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} product reviews')
        )
