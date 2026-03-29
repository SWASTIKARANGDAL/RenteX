"""
Management command to seed the database with sample data for testing.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🌱 Seeding database...'))

        self.create_categories()
        self.create_users()
        self.create_products()
        self.create_bookings()

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!\n'))
        self.stdout.write('=' * 50)
        self.stdout.write('Demo Credentials:')
        self.stdout.write('  Admin  → admin@rentex.com  / admin123')
        self.stdout.write('  Owner  → owner@rentex.com  / owner123')
        self.stdout.write('  Owner2 → owner2@rentex.com / owner123')
        self.stdout.write('  Renter → renter@rentex.com / renter123')
        self.stdout.write('=' * 50)

    def create_categories(self):
        from apps.products.models import Category
        categories_data = [
            {'name': 'Laptops', 'slug': 'laptops', 'icon': 'bi-laptop', 'order': 1},
            {'name': 'Cameras', 'slug': 'cameras', 'icon': 'bi-camera', 'order': 2},
            {'name': 'Smartphones', 'slug': 'phones', 'icon': 'bi-phone', 'order': 3},
            {'name': 'Gaming Consoles', 'slug': 'gaming', 'icon': 'bi-controller', 'order': 4},
            {'name': 'Drones', 'slug': 'drones', 'icon': 'bi-airplane', 'order': 5},
            {'name': 'Audio Equipment', 'slug': 'audio', 'icon': 'bi-headphones', 'order': 6},
            {'name': 'Projectors', 'slug': 'projectors', 'icon': 'bi-display', 'order': 7},
            {'name': 'VR Headsets', 'slug': 'vr', 'icon': 'bi-badge-vr', 'order': 8},
        ]
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  📂 Created category: {cat.name}')
        self.stdout.write(self.style.SUCCESS('✓ Categories created'))

    def create_users(self):
        # Superadmin
        if not User.objects.filter(email='admin@rentex.com').exists():
            User.objects.create_superuser(
                username='admin', email='admin@rentex.com',
                password='admin123', first_name='Admin', last_name='RenteX',
                role='owner', is_verified=True
            )
            self.stdout.write('  👤 Created admin user')

        # Owners
        owners_data = [
            {'username': 'techowner', 'email': 'owner@rentex.com', 'first_name': 'Rajesh', 'last_name': 'Kumar', 'city': 'Bengaluru', 'state': 'Karnataka'},
            {'username': 'gadgetguru', 'email': 'owner2@rentex.com', 'first_name': 'Priya', 'last_name': 'Sharma', 'city': 'Mumbai', 'state': 'Maharashtra'},
        ]
        for od in owners_data:
            if not User.objects.filter(email=od['email']).exists():
                User.objects.create_user(
                    password='owner123', role='owner', is_verified=True,
                    bio='Verified electronics owner on RenteX.', **od
                )
                self.stdout.write(f"  👤 Created owner: {od['first_name']}")

        # Renters
        renters_data = [
            {'username': 'renter1', 'email': 'renter@rentex.com', 'first_name': 'Amit', 'last_name': 'Patel', 'city': 'Bengaluru', 'state': 'Karnataka'},
            {'username': 'renter2', 'email': 'renter2@rentex.com', 'first_name': 'Sneha', 'last_name': 'Singh', 'city': 'Delhi', 'state': 'Delhi'},
        ]
        for rd in renters_data:
            if not User.objects.filter(email=rd['email']).exists():
                User.objects.create_user(password='renter123', role='renter', **rd)
                self.stdout.write(f"  👤 Created renter: {rd['first_name']}")

        self.stdout.write(self.style.SUCCESS('✓ Users created'))

    def create_products(self):
        from apps.products.models import Product, Category, ProductSpecification
        owner1 = User.objects.get(email='owner@rentex.com')
        owner2 = User.objects.get(email='owner2@rentex.com')

        products_data = [
            {
                'owner': owner1,
                'category_slug': 'laptops',
                'name': 'MacBook Pro 16" M3',
                'description': 'Apple MacBook Pro 16-inch with M3 Pro chip. Perfect for video editing, software development, and creative work. Comes with charger and sleeve. Battery life 18+ hours.',
                'brand': 'Apple',
                'model_number': 'MacBook Pro 16" M3 Pro',
                'condition': 'like_new',
                'price_per_day': Decimal('999'),
                'price_per_week': Decimal('5999'),
                'price_per_month': Decimal('19999'),
                'deposit_amount': Decimal('5000'),
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'is_featured': True,
                'specs': [('RAM', '36GB'), ('Storage', '512GB SSD'), ('Display', '16.2" Liquid Retina XDR'), ('OS', 'macOS Sonoma')],
            },
            {
                'owner': owner1,
                'category_slug': 'cameras',
                'name': 'Sony Alpha A7R V',
                'description': 'Full-frame mirrorless camera with 61MP sensor. Ideal for professional photography and videography. Includes 50mm lens, 2 batteries, and camera bag.',
                'brand': 'Sony',
                'model_number': 'ILCE-7RM5',
                'condition': 'good',
                'price_per_day': Decimal('1499'),
                'price_per_week': Decimal('8499'),
                'price_per_month': Decimal('29999'),
                'deposit_amount': Decimal('10000'),
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'is_featured': True,
                'specs': [('Sensor', '61MP BSI CMOS'), ('Video', '8K RAW'), ('Stabilization', '8-stop IBIS'), ('Mount', 'Sony E-Mount')],
            },
            {
                'owner': owner1,
                'category_slug': 'gaming',
                'name': 'PlayStation 5 Bundle',
                'description': 'Sony PlayStation 5 disc edition with 2 DualSense controllers and 5 games including Spider-Man 2 and God of War. Perfect for gaming events or trying before buying.',
                'brand': 'Sony',
                'model_number': 'CFI-1218A',
                'condition': 'like_new',
                'price_per_day': Decimal('599'),
                'price_per_week': Decimal('3499'),
                'price_per_month': Decimal('11999'),
                'deposit_amount': Decimal('3000'),
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'is_featured': True,
                'specs': [('CPU', 'AMD Zen 2 8-core'), ('GPU', 'AMD RDNA 2 10.3 TFLOPS'), ('Storage', '825GB SSD'), ('Optical Drive', 'Yes')],
            },
            {
                'owner': owner2,
                'category_slug': 'drones',
                'name': 'DJI Mavic 3 Pro',
                'description': 'Professional drone with Hasselblad camera. Triple-camera system with 4/3 CMOS sensor. 43-minute flight time. Perfect for aerial photography and videography.',
                'brand': 'DJI',
                'model_number': 'Mavic 3 Pro',
                'condition': 'like_new',
                'price_per_day': Decimal('2499'),
                'price_per_week': Decimal('14999'),
                'price_per_month': Decimal('49999'),
                'deposit_amount': Decimal('15000'),
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'is_featured': True,
                'specs': [('Camera', 'Hasselblad 4/3 CMOS'), ('Max Speed', '21 m/s'), ('Flight Time', '43 min'), ('Range', '15 km')],
            },
            {
                'owner': owner2,
                'category_slug': 'laptops',
                'name': 'Dell XPS 15 OLED',
                'description': 'Dell XPS 15 with stunning OLED display. Intel i9 processor, RTX 4070 GPU. Excellent for creative professionals, data scientists, and power users.',
                'brand': 'Dell',
                'model_number': 'XPS 15 9530',
                'condition': 'good',
                'price_per_day': Decimal('799'),
                'price_per_week': Decimal('4799'),
                'price_per_month': Decimal('15999'),
                'deposit_amount': Decimal('4000'),
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'is_featured': False,
                'specs': [('CPU', 'Intel i9-13900H'), ('GPU', 'NVIDIA RTX 4070'), ('RAM', '32GB DDR5'), ('Display', '15.6" OLED 3.5K')],
            },
            {
                'owner': owner1,
                'category_slug': 'audio',
                'name': 'Sony WH-1000XM5 + DAC Bundle',
                'description': 'Industry-leading noise cancellation headphones with Hi-Res audio DAC. Perfect for studios, travel, or focused work. Includes carrying case and all cables.',
                'brand': 'Sony',
                'model_number': 'WH-1000XM5',
                'condition': 'like_new',
                'price_per_day': Decimal('299'),
                'price_per_week': Decimal('1799'),
                'price_per_month': Decimal('5999'),
                'deposit_amount': Decimal('1000'),
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'is_featured': False,
                'specs': [('Driver', '30mm'), ('Battery', '30 hours'), ('ANC', 'Industry Leading'), ('Connectivity', 'Bluetooth 5.2')],
            },
            {
                'owner': owner2,
                'category_slug': 'phones',
                'name': 'iPhone 15 Pro Max',
                'description': 'Apple iPhone 15 Pro Max 256GB in Natural Titanium. Perfect for product photography with 48MP camera system, or as a backup device during travel.',
                'brand': 'Apple',
                'model_number': 'iPhone 15 Pro Max',
                'condition': 'like_new',
                'price_per_day': Decimal('499'),
                'price_per_week': Decimal('2999'),
                'price_per_month': Decimal('9999'),
                'deposit_amount': Decimal('5000'),
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'is_featured': False,
                'specs': [('Chip', 'A17 Pro'), ('Camera', '48MP Main + 12MP Ultra Wide'), ('Storage', '256GB'), ('Display', '6.7" Super Retina XDR')],
            },
            {
                'owner': owner2,
                'category_slug': 'projectors',
                'name': 'Epson 4K Laser Projector',
                'description': 'Epson EF-21 4K laser projector with 2500 lumens. Ideal for events, presentations, home cinema setups, or outdoor screenings. Includes HDMI cable and remote.',
                'brand': 'Epson',
                'model_number': 'EF-21',
                'condition': 'good',
                'price_per_day': Decimal('999'),
                'price_per_week': Decimal('5999'),
                'price_per_month': Decimal('19999'),
                'deposit_amount': Decimal('5000'),
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'is_featured': False,
                'specs': [('Resolution', '4K UHD'), ('Brightness', '2500 lumens'), ('Laser Life', '20,000 hours'), ('Throw Ratio', '1.35:1 to 2.84:1')],
            },
        ]

        for pd in products_data:
            specs = pd.pop('specs', [])
            cat_slug = pd.pop('category_slug')
            cat = Category.objects.get(slug=cat_slug)
            product, created = Product.objects.get_or_create(
                name=pd['name'],
                owner=pd['owner'],
                defaults={**pd, 'category': cat}
            )
            if created:
                # Add specs
                for key, value in specs:
                    ProductSpecification.objects.create(product=product, key=key, value=value)
                self.stdout.write(f'  📦 Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS('✓ Products created'))

    def create_bookings(self):
        from apps.bookings.models import Booking
        from apps.products.models import Product
        from apps.payments.models import Payment
        from datetime import date, timedelta

        renter = User.objects.get(email='renter@rentex.com')
        renter2 = User.objects.filter(email='renter2@rentex.com').first()
        products = list(Product.objects.all())

        if not products:
            return

        bookings_data = [
            {
                'renter': renter,
                'product': products[0],
                'start_date': date.today() + timedelta(days=3),
                'end_date': date.today() + timedelta(days=8),
                'status': 'confirmed',
                'paid': True,
            },
            {
                'renter': renter,
                'product': products[1],
                'start_date': date.today() - timedelta(days=10),
                'end_date': date.today() - timedelta(days=5),
                'status': 'completed',
                'paid': True,
            },
            {
                'renter': renter,
                'product': products[2] if len(products) > 2 else products[0],
                'start_date': date.today() + timedelta(days=15),
                'end_date': date.today() + timedelta(days=18),
                'status': 'pending',
                'paid': False,
            },
        ]

        for bd in bookings_data:
            paid = bd.pop('paid')
            product = bd['product']
            total_days = (bd['end_date'] - bd['start_date']).days or 1
            rental_amount = product.get_price_for_days(total_days)
            from decimal import Decimal
            total = Decimal(rental_amount) + product.deposit_amount

            booking, created = Booking.objects.get_or_create(
                renter=bd['renter'],
                product=bd['product'],
                start_date=bd['start_date'],
                defaults={
                    'end_date': bd['end_date'],
                    'status': bd['status'],
                    'total_days': total_days,
                    'rental_amount': rental_amount,
                    'deposit_amount': product.deposit_amount,
                    'total_amount': total,
                }
            )
            if created:
                if paid:
                    from django.utils import timezone as tz
                    Payment.objects.create(
                        booking=booking,
                        amount=booking.total_amount,
                        status='completed',
                        gateway='razorpay',
                        gateway_payment_id=f'pay_demo_{booking.booking_number}',
                        paid_at=tz.now(),
                    )
                self.stdout.write(f'  📅 Created booking: {booking.booking_number}')

        self.stdout.write(self.style.SUCCESS('✓ Bookings created'))
