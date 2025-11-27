from django.core.management.base import BaseCommand
from products.models import Product, Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Create sample products with proper stock and details'

    def handle(self, *args, **options):
        # Create categories if they don't exist
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Mobile', 'slug': 'mobile'},
            {'name': 'Fashion', 'slug': 'fashion'},
            {'name': 'Home & Kitchen', 'slug': 'home-kitchen'},
            {'name': 'Books', 'slug': 'books'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Sample products data
        products_data = [
            {
                'name': 'iPhone 14',
                'category': 'mobile',
                'description': 'Latest iPhone with advanced camera system and A16 Bionic chip.',
                'short_description': 'iPhone 14 with 128GB storage',
                'price': 79900.00,
                'mrp': 89900.00,
                'discount_percentage': 11,
                'stock': 25,
                'is_active': True,
                'featured': True
            },
            {
                'name': 'Samsung Galaxy S23',
                'category': 'mobile',
                'description': 'Premium Android smartphone with excellent camera and performance.',
                'short_description': 'Galaxy S23 with 256GB storage',
                'price': 74999.00,
                'mrp': 84999.00,
                'discount_percentage': 12,
                'stock': 30,
                'is_active': True,
                'featured': True
            },
            {
                'name': 'MacBook Air M2',
                'category': 'electronics',
                'description': 'Lightweight laptop with M2 chip for exceptional performance.',
                'short_description': 'MacBook Air with M2 chip',
                'price': 114900.00,
                'mrp': 119900.00,
                'discount_percentage': 4,
                'stock': 15,
                'is_active': True,
                'featured': True
            },
            {
                'name': 'Sony WH-1000XM4 Headphones',
                'category': 'electronics',
                'description': 'Industry-leading noise canceling headphones with premium sound.',
                'short_description': 'Wireless noise canceling headphones',
                'price': 24990.00,
                'mrp': 29990.00,
                'discount_percentage': 17,
                'stock': 40,
                'is_active': True,
                'featured': False
            },
            {
                'name': 'Nike Air Max 270',
                'category': 'fashion',
                'description': 'Comfortable running shoes with Air Max technology.',
                'short_description': 'Nike running shoes',
                'price': 12995.00,
                'mrp': 14995.00,
                'discount_percentage': 13,
                'stock': 50,
                'is_active': True,
                'featured': False
            },
            {
                'name': 'Instant Pot Duo 7-in-1',
                'category': 'home-kitchen',
                'description': '7-in-1 electric pressure cooker for versatile cooking.',
                'short_description': 'Multi-use pressure cooker',
                'price': 8999.00,
                'mrp': 12999.00,
                'discount_percentage': 31,
                'stock': 20,
                'is_active': True,
                'featured': False
            },
            {
                'name': 'The Psychology of Money',
                'category': 'books',
                'description': 'Timeless lessons on wealth, greed, and happiness by Morgan Housel.',
                'short_description': 'Bestselling finance book',
                'price': 299.00,
                'mrp': 399.00,
                'discount_percentage': 25,
                'stock': 100,
                'is_active': True,
                'featured': False
            },
            {
                'name': 'iPad Pro 11-inch',
                'category': 'electronics',
                'description': 'Powerful tablet with M2 chip and Liquid Retina display.',
                'short_description': 'iPad Pro with M2 chip',
                'price': 81900.00,
                'mrp': 89900.00,
                'discount_percentage': 9,
                'stock': 18,
                'is_active': True,
                'featured': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for product_data in products_data:
            category = Category.objects.get(slug=product_data['category'])
            slug = slugify(product_data['name'])
            
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': product_data['name'],
                    'category': category,
                    'description': product_data['description'],
                    'short_description': product_data['short_description'],
                    'price': product_data['price'],
                    'mrp': product_data['mrp'],
                    'discount_percentage': product_data['discount_percentage'],
                    'stock': product_data['stock'],
                    'is_active': product_data['is_active'],
                    'featured': product_data['featured']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created product: {product.name}')
            else:
                # Update existing product with new stock and details
                for field, value in product_data.items():
                    if field != 'category':
                        if field == 'category':
                            setattr(product, field, category)
                        else:
                            setattr(product, field, value)
                product.save()
                updated_count += 1
                self.stdout.write(f'Updated product: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed products: {created_count} created, {updated_count} updated'
            )
        )
