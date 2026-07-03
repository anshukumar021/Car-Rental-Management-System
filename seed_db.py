import os
import django
from datetime import date, timedelta
from PIL import Image, ImageDraw

# Initialize django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_rental.settings")
django.setup()

from rental.models import User, Car, Booking, Category, Payment

def create_dummy_car_image(filepath, brand_name, bg_color):
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
        print(f"Keeping existing real image at {filepath}")
        return
    # Generates a simple styled placeholder image
    img = Image.new('RGB', (800, 500), color=bg_color)
    d = ImageDraw.Draw(img)
    
    d.rectangle([(20, 20), (780, 480)], outline=(255, 255, 255), width=2)
    d.line([(400, 0), (400, 500)], fill=(255, 255, 255, 20), width=1)
    d.line([(0, 250), (800, 250)], fill=(255, 255, 255, 20), width=1)
    d.ellipse([(250, 100), (550, 400)], outline=(255, 255, 255), width=3)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)
    print(f"Generated dummy image at {filepath}")

def seed():
    print("Seeding database (Module 4)...")
    
    # 1. Get or create a test user
    user = User.objects.filter(email="lightuser@example.com").first()
    if not user:
        user = User.objects.filter(is_superuser=False).first()
    if not user:
        user = User.objects.create_user(
            email="lightuser@example.com",
            name="Light User",
            mobile="9876543210",
            password="TestPassword123"
        )
        print(f"Created test user: {user.email}")
    else:
        print(f"Using existing test user: {user.email}")

    # Get or create admin user
    admin_user = User.objects.filter(email="admin@example.com").first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            name="Admin User",
            password="adminpassword123"
        )
        print(f"Created admin user: {admin_user.email}")
    else:
        print(f"Using existing admin user: {admin_user.email}")

    # Get or create staff user
    staff_user = User.objects.filter(email="staff@example.com").first()
    if not staff_user:
        staff_user = User.objects.create_user(
            email="staff@example.com",
            name="Staff User",
            mobile="9876543211",
            password="staffpassword123",
            role="staff",
            is_staff=True
        )
        print(f"Created staff user: {staff_user.email}")
    else:
        print(f"Using existing staff user: {staff_user.email}")

    # Clear old data
    Booking.objects.all().delete()
    Car.objects.all().delete()
    Category.objects.all().delete()
    print("Cleared existing tables.")

    # 2. Create the 6 categories
    categories_data = [
        {"name": "Hatchback", "description": "Compact and agile vehicles with a rear hatch door, perfect for urban commuting and tight parking."},
        {"name": "Sedan", "description": "Classic three-box passenger cars featuring a separate passenger cabin, engine bay, and cargo trunk."},
        {"name": "SUV", "description": "Sport Utility Vehicles built with elevated ride heights, robust construction, and spacious cabins."},
        {"name": "Luxury", "description": "Premium automobiles delivering top-tier comfort, cutting-edge technology features, and prestige styling."},
        {"name": "Electric Vehicle", "description": "Modern eco-friendly vehicles run entirely on clean electric batteries without internal combustion."},
        {"name": "Sports Car", "description": "High-performance speed vehicles engineered for responsive handling, aerodynamics, and driver engagement."}
    ]
    
    cats = {}
    for cat_data in categories_data:
        cat = Category.objects.create(**cat_data)
        cats[cat.name] = cat
        print(f"Created Category: {cat.name}")

    # Paths to dummy images
    media_dir = os.path.join("media", "cars")
    img_creta = os.path.join(media_dir, "creta.png")
    img_city = os.path.join(media_dir, "city.png")
    img_swift = os.path.join(media_dir, "swift.png")
    img_m3 = os.path.join(media_dir, "m3.png")
    img_a6 = os.path.join(media_dir, "a6.png")
    img_thar = os.path.join(media_dir, "thar.png")
    img_nexon = os.path.join(media_dir, "nexon.png")
    img_baleno = os.path.join(media_dir, "baleno.png")
    img_comet = os.path.join(media_dir, "comet.png")
    img_sonet = os.path.join(media_dir, "sonet.png")
    img_dzire = os.path.join(media_dir, "dzire.png")
    img_altroz = os.path.join(media_dir, "altroz.png")

    # Generate the images
    create_dummy_car_image(img_creta, "Creta", "#006666")
    create_dummy_car_image(img_city, "City", "#400080")
    create_dummy_car_image(img_swift, "Swift", "#800000")
    create_dummy_car_image(img_m3, "M3", "#2c3e50")
    create_dummy_car_image(img_a6, "A6", "#1a5276")
    create_dummy_car_image(img_thar, "Thar", "#2e4053")
    create_dummy_car_image(img_nexon, "Nexon", "#239b56")
    create_dummy_car_image(img_baleno, "Baleno", "#1f618d")
    create_dummy_car_image(img_comet, "Comet", "#d35400")
    create_dummy_car_image(img_sonet, "Sonet", "#7d3c98")
    create_dummy_car_image(img_dzire, "Dzire", "#273746")
    create_dummy_car_image(img_altroz, "Altroz", "#9a7d0a")

    # 3. Create Cars data linked to Categories
    cars_data = [
        {
            "name": "Hyundai Creta",
            "brand": "Hyundai",
            "model": "Creta SX",
            "category": cats["SUV"],
            "year": 2024,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "seating_capacity": 5,
            "rent_per_day": 2500.00,
            "image": "cars/creta.png",
            "status": "Available"
        },
        {
            "name": "Honda City",
            "brand": "Honda",
            "model": "City VX",
            "category": cats["Sedan"],
            "year": 2023,
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "seating_capacity": 5,
            "rent_per_day": 2200.00,
            "image": "cars/city.png",
            "status": "Available"
        },
        {
            "name": "Maruti Swift",
            "brand": "Maruti",
            "model": "Swift LXI",
            "category": cats["Hatchback"],
            "year": 2022,
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "seating_capacity": 5,
            "rent_per_day": 1200.00,
            "image": "cars/swift.png",
            "status": "Available"
        },
        {
            "name": "BMW M3",
            "brand": "BMW",
            "model": "M3 Competition",
            "category": cats["Sports Car"],
            "year": 2024,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "seating_capacity": 4,
            "rent_per_day": 8500.00,
            "image": "cars/m3.png",
            "status": "Maintenance"
        },
        {
            "name": "Audi A6",
            "brand": "Audi",
            "model": "A6 Premium",
            "category": cats["Luxury"],
            "year": 2024,
            "fuel_type": "Diesel",
            "transmission": "Automatic",
            "seating_capacity": 5,
            "rent_per_day": 7500.00,
            "image": "cars/a6.png",
            "status": "Available"
        },
        {
            "name": "Mahindra Thar",
            "brand": "Mahindra",
            "model": "Thar LX",
            "category": cats["SUV"],
            "year": 2023,
            "fuel_type": "Diesel",
            "transmission": "Manual",
            "seating_capacity": 4,
            "rent_per_day": 2000.00,
            "image": "cars/thar.png",
            "status": "Available"
        },
        {
            "name": "Tata Nexon",
            "brand": "Tata",
            "model": "Nexon Creative",
            "category": cats["SUV"],
            "year": 2024,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "seating_capacity": 5,
            "rent_per_day": 1800.00,
            "image": "cars/nexon.png",
            "status": "Available"
        },
        {
            "name": "Maruti Baleno",
            "brand": "Maruti",
            "model": "Baleno Alpha",
            "category": cats["Hatchback"],
            "year": 2023,
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "seating_capacity": 5,
            "rent_per_day": 1100.00,
            "image": "cars/baleno.png",
            "status": "Available"
        },
        {
            "name": "MG Comet EV",
            "brand": "MG",
            "model": "Comet Plush",
            "category": cats["Electric Vehicle"],
            "year": 2024,
            "fuel_type": "Electric",
            "transmission": "Automatic",
            "seating_capacity": 4,
            "rent_per_day": 900.00,
            "image": "cars/comet.png",
            "status": "Available"
        },
        {
            "name": "Kia Sonet",
            "brand": "Kia",
            "model": "Sonet HTX",
            "category": cats["SUV"],
            "year": 2023,
            "fuel_type": "Diesel",
            "transmission": "Automatic",
            "seating_capacity": 5,
            "rent_per_day": 1600.00,
            "image": "cars/sonet.png",
            "status": "Available"
        },
        {
            "name": "Maruti Dzire",
            "brand": "Maruti",
            "model": "Dzire ZXI",
            "category": cats["Sedan"],
            "year": 2023,
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "seating_capacity": 5,
            "rent_per_day": 1300.00,
            "image": "cars/dzire.png",
            "status": "Available"
        },
        {
            "name": "Tata Altroz",
            "brand": "Tata",
            "model": "Altroz XZ",
            "category": cats["Hatchback"],
            "year": 2023,
            "fuel_type": "Diesel",
            "transmission": "Manual",
            "seating_capacity": 5,
            "rent_per_day": 1200.00,
            "image": "cars/altroz.png",
            "status": "Available"
        },
    ]
    
    cars = []
    for c_data in cars_data:
        car = Car.objects.create(**c_data)
        cars.append(car)
        print(f"Created Car: {car.name} (Category: {car.category.name}, Rent: Rs.{car.rent_per_day})")

    # 4. Create Bookings
    today = date.today()
    
    # Booking 1: Confirmed booking starting today
    b1 = Booking.objects.create(
        user=user,
        car=cars[0],  # Hyundai Creta
        pickup_date=today,
        return_date=today + timedelta(days=4),
        total_days=4,
        status="confirmed",
        total_price=10000.00
    )
    Payment.objects.create(
        booking=b1,
        amount=b1.total_price,
        payment_method="Credit Card",
        status="Paid",
        transaction_id="TXN-CONF-77123"
    )
    print(f"Created active confirmed booking: {b1} with completed Payment")

    # Booking 2: Completed booking from last month
    b2 = Booking.objects.create(
        user=user,
        car=cars[1],  # Honda City
        pickup_date=today - timedelta(days=30),
        return_date=today - timedelta(days=26),
        total_days=4,
        status="completed",
        total_price=8800.00
    )
    Payment.objects.create(
        booking=b2,
        amount=b2.total_price,
        payment_method="UPI",
        status="Paid",
        transaction_id="TXN-COMP-99128"
    )
    print(f"Created completed booking: {b2} with completed Payment")

    # Booking 3: Pending booking starting in 5 days
    b3 = Booking.objects.create(
        user=user,
        car=cars[2],  # Maruti Swift
        pickup_date=today + timedelta(days=5),
        return_date=today + timedelta(days=10),
        total_days=5,
        status="pending",
        total_price=6000.00
    )
    Payment.objects.create(
        booking=b3,
        amount=b3.total_price,
        payment_method="Credit Card",
        status="Pending"
    )
    print(f"Created pending booking: {b3} with pending Payment")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
