from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )

    username = None
    email = models.EmailField(unique=True, verbose_name="Email Address")
    name = models.CharField(max_length=255, verbose_name="Full Name")
    mobile = models.CharField(max_length=15, verbose_name="Mobile Number")
    license_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Driving License Number")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer', verbose_name="Role")
    is_license_verified = models.BooleanField(default=False, verbose_name="License Verified")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.get_role_display()}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return self.name


class Car(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Booked', 'Booked'),
        ('Maintenance', 'Maintenance'),
        ('Inactive', 'Inactive'),
    )
    name = models.CharField(max_length=150, verbose_name="Vehicle Name")
    brand = models.CharField(max_length=100, verbose_name="Brand")
    model = models.CharField(max_length=100, verbose_name="Model")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars', verbose_name="Category")
    year = models.IntegerField(verbose_name="Year")
    fuel_type = models.CharField(max_length=50, verbose_name="Fuel Type")
    transmission = models.CharField(max_length=50, verbose_name="Transmission")
    seating_capacity = models.IntegerField(verbose_name="Seating Capacity")
    rent_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Rent Per Day")
    image = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name="Vehicle Image")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Available', verbose_name="Status")

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) - {self.status}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('confirmed', 'Booked'),
        ('booked', 'Booked'),
        ('picked_up', 'Picked Up'),
        ('in_use', 'In Use'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Customer")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings', verbose_name="Vehicle")
    pickup_date = models.DateField(verbose_name="Pickup Date")
    return_date = models.DateField(verbose_name="Return Date")
    total_days = models.IntegerField(default=1, verbose_name="Total Days")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Price")
    damage_report = models.TextField(blank=True, null=True, verbose_name="Damage Report")
    pickup_time = models.DateTimeField(blank=True, null=True, verbose_name="Actual Pickup Time")
    return_time = models.DateTimeField(blank=True, null=True, verbose_name="Actual Return Time")

    def __str__(self):
        return f"Booking #{self.id} - {self.user.name} - {self.car.brand} {self.car.model} ({self.get_status_display()})"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Refunded', 'Refunded'),
    )
    METHOD_CHOICES = (
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
    )
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', verbose_name="Booking")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    payment_method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='Credit Card', verbose_name="Payment Method")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Status")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Transaction ID")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Payment Date")

    def __str__(self):
        return f"Payment #{self.id} for Booking #{self.booking.id} - {self.get_status_display()}"


class Maintenance(models.Model):
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='maintenances', verbose_name="Vehicle")
    service_date = models.DateField(verbose_name="Service Date")
    service_type = models.CharField(max_length=150, verbose_name="Service Type")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Cost")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled', verbose_name="Status")
    notes = models.TextField(blank=True, null=True, verbose_name="Service Notes")

    def __str__(self):
        return f"Maintenance #{self.id} for {self.car.brand} {self.car.model} ({self.status})"


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review', verbose_name="Booking")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Customer")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews', verbose_name="Vehicle")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Rating (1-5)")
    comment = models.TextField(verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Review Date")

    def __str__(self):
        return f"Review for Booking #{self.booking.id} - {self.user.name} ({self.rating} stars)"
