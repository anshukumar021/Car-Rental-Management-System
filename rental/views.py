import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import CustomerRegistrationForm, UserLoginForm, CarForm, CategoryForm, BookingForm, UserProfileForm, MaintenanceForm
from .models import Car, Booking, Category, Payment, User, Maintenance, Review

# Role restriction decorator for Staff and Admin only
def role_required(allowed_roles):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("<h3>Access Denied</h3><p>You do not have administrative permissions to perform this action.</p>")
        return _wrapped_view
    return decorator

def front_page_view(request):
    featured_cars = Car.objects.filter(status='Available').order_by('rent_per_day')[:3]
    categories = Category.objects.all()
    return render(request, 'rental/front_page.html', {
        'featured_cars': featured_cars,
        'categories': categories
    })


def about_page_view(request):
    return render(request, 'rental/about.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email
            try:
                send_mail(
                    subject="Welcome to AutoDrive!",
                    message=f"Hi {user.name},\n\nWelcome to AutoDrive! Your account has been successfully created.\n\nEnjoy renting your favorite vehicles with us!\n\nBest regards,\nThe AutoDrive Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
                
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = CustomerRegistrationForm()
        
    return render(request, 'rental/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = UserLoginForm()
        
    return render(request, 'rental/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    is_staff = request.user.role in ['admin', 'staff'] or request.user.is_superuser
    
    available_cars = Car.objects.filter(status='Available').count()
    active_statuses = ['confirmed', 'booked', 'picked_up', 'in_use', 'returned']
    
    if is_staff:
        # Standard Counts
        active_bookings = Booking.objects.filter(status__in=active_statuses).count()
        completed_rentals = Booking.objects.filter(status='completed').count()
        pending_requests = Booking.objects.filter(status='pending').count()
        recent_bookings = Booking.objects.all().order_by('-pickup_date')[:5]
        
        # Admin Cards (Module 15)
        total_vehicles = Car.objects.count()
        total_customers = User.objects.filter(role='customer').count()
        total_bookings = Booking.objects.count()
        
        from django.db.models import Sum
        revenue_sum = Payment.objects.filter(status='Paid').aggregate(total=Sum('amount'))['total'] or 0
        
        pending_payments_count = Payment.objects.filter(status='Pending').count()
        pending_payments_amount = Payment.objects.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0
        
        # Charts Data (Module 15)
        import datetime
        current_year = datetime.date.today().year
        
        # 1. Monthly Revenue Chart (current year)
        payments_this_year = Payment.objects.filter(status='Paid', payment_date__year=current_year)
        monthly_revenue_data = {i: 0.0 for i in range(1, 13)}
        for p in payments_this_year:
            month = p.payment_date.month
            monthly_revenue_data[month] += float(p.amount)
            
        revenue_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        revenue_values = [monthly_revenue_data[i] for i in range(1, 13)]
        
        # 2. Vehicle Usage Chart
        car_status_data = {
            'Available': Car.objects.filter(status='Available').count(),
            'Booked': Car.objects.filter(status='Booked').count(),
            'Maintenance': Car.objects.filter(status='Maintenance').count(),
            'Inactive': Car.objects.filter(status='Inactive').count(),
        }
        vehicle_usage_labels = list(car_status_data.keys())
        vehicle_usage_values = list(car_status_data.values())
        
        # 3. Booking Trends Chart (current year)
        bookings_this_year = Booking.objects.filter(pickup_date__year=current_year)
        monthly_bookings_data = {i: 0 for i in range(1, 13)}
        for b in bookings_this_year:
            month = b.pickup_date.month
            monthly_bookings_data[month] += 1
            
        booking_trend_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        booking_trend_values = [monthly_bookings_data[i] for i in range(1, 13)]
        
        context = {
            'is_staff': True,
            'role': request.user.role,
            'name': request.user.name,
            'recent_bookings': recent_bookings,
            
            # Cards
            'total_vehicles': total_vehicles,
            'total_customers': total_customers,
            'total_bookings': total_bookings,
            'revenue_sum': revenue_sum,
            'pending_payments_count': pending_payments_count,
            'pending_payments_amount': pending_payments_amount,
            
            # Charts
            'revenue_labels': revenue_labels,
            'revenue_values': revenue_values,
            'vehicle_usage_labels': vehicle_usage_labels,
            'vehicle_usage_values': vehicle_usage_values,
            'booking_trend_labels': booking_trend_labels,
            'booking_trend_values': booking_trend_values,
        }
    else:
        # Customer Context
        active_bookings = Booking.objects.filter(user=request.user, status__in=active_statuses).count()
        completed_rentals = Booking.objects.filter(user=request.user, status='completed').count()
        pending_requests = Booking.objects.filter(user=request.user, status='pending').count()
        recent_bookings = Booking.objects.filter(user=request.user).order_by('-pickup_date')[:5]
        
        context = {
            'is_staff': False,
            'role': request.user.role,
            'name': request.user.name,
            'available_cars': available_cars,
            'active_bookings': active_bookings,
            'completed_rentals': completed_rentals,
            'pending_requests': pending_requests,
            'recent_bookings': recent_bookings,
        }
        
    return render(request, 'rental/dashboard.html', context)

# Vehicle Inventory Management Views
def car_list_view(request):
    query = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()
    sort_by = request.GET.get('sort_by', '').strip()
    available_only = request.GET.get('available_only') == 'on'
    luxury_only = request.GET.get('luxury_only') == 'on'
    electric_only = request.GET.get('electric_only') == 'on'
    category_filter = request.GET.get('category', '').strip()
    
    cars = Car.objects.all()
    
    if query:
        from django.db.models import Q
        cars = cars.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query) |
            Q(category__name__icontains=query) |
            Q(fuel_type__icontains=query)
        )
        
    if start_date and end_date:
        from datetime import datetime
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            if start <= end:
                overlapping_bookings = Booking.objects.exclude(
                    status__in=['completed', 'cancelled']
                ).filter(
                    pickup_date__lte=end,
                    return_date__gte=start
                ).values_list('car_id', flat=True)
                cars = cars.exclude(id__in=overlapping_bookings)
        except ValueError:
            pass

    if category_filter:
        if category_filter.isdigit():
            cars = cars.filter(category_id=int(category_filter))
        else:
            cars = cars.filter(category__name__iexact=category_filter)

    if available_only:
        cars = cars.filter(status='Available')
        
    if luxury_only:
        cars = cars.filter(category__name='Luxury')
        
    if electric_only:
        cars = cars.filter(category__name='Electric Vehicle')

    if sort_by == 'price_asc':
        cars = cars.order_by('rent_per_day')
    elif sort_by == 'price_desc':
        cars = cars.order_by('-rent_per_day')
    else:
        cars = cars.order_by('brand', 'model')

    context = {
        'cars': cars,
        'query': query,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'available_only': available_only,
        'luxury_only': luxury_only,
        'electric_only': electric_only,
        'category_filter': category_filter,
    }
    return render(request, 'rental/car_list.html', context)

def car_detail_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'rental/car_detail.html', {'car': car})

@role_required(['staff', 'admin'])
def car_create_view(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('car_list')
    else:
        form = CarForm()
    return render(request, 'rental/car_form.html', {'form': form, 'title': 'Add Vehicle'})

@role_required(['staff', 'admin'])
def car_update_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm(instance=car)
    return render(request, 'rental/car_form.html', {'form': form, 'title': 'Edit Vehicle', 'car': car})

@role_required(['staff', 'admin'])
def car_delete_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        return redirect('car_list')
    return render(request, 'rental/car_confirm_delete.html', {'car': car})

# Category Management Views
@login_required
def category_list_view(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'rental/category_list.html', {'categories': categories})

@role_required(['staff', 'admin'])
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'rental/category_form.html', {'form': form, 'title': 'Add Category'})

@role_required(['staff', 'admin'])
def category_update_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'rental/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})

@role_required(['staff', 'admin'])
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'rental/category_confirm_delete.html', {'category': category})

# Customer actions for booking and history
@login_required
def book_car_view(request):
    car_id = request.GET.get('car_id')
    preselected_car = None
    if car_id:
        preselected_car = get_object_or_404(Car, pk=car_id, status='Available')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            if preselected_car:
                booking.car = preselected_car
                
            delta = booking.return_date - booking.pickup_date
            days = max(delta.days, 1)
            booking.total_price = booking.car.rent_per_day * days
            booking.total_days = days
            booking.save()
            # Create a pending Payment record for this booking
            Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                payment_method="Credit Card",
                status="Pending"
            )
            
            # Automatically send Booking Request Received email
            try:
                send_mail(
                    subject=f"Booking Request Received - #BK-{booking.id}",
                    message=f"Hi {booking.user.name},\n\nWe have successfully received your booking request for the {booking.car.brand} {booking.car.model}!\n\nBooking Summary:\n- Booking ID: #BK-{booking.id}\n- Vehicle: {booking.car.brand} {booking.car.model}\n- Pickup Date: {booking.pickup_date}\n- Return Date: {booking.return_date}\n- Estimated Price: ₹{booking.total_price}\n- Status: Pending Approval\n\nOur staff will review and approve your request shortly. You can check the details on your Dashboard.\n\nBest regards,\nThe AutoDrive Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
                
            return redirect('dashboard')
    else:
        initial_data = {}
        if preselected_car:
            initial_data['car'] = preselected_car
        form = BookingForm(initial=initial_data)

    context = {
        'form': form,
        'preselected_car': preselected_car,
        'cars': Car.objects.filter(status='Available')
    }
    return render(request, 'rental/book_car.html', context)

@login_required
def view_history_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-pickup_date')
    return render(request, 'rental/history.html', {'bookings': bookings})

@login_required
def download_invoice_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser or booking.user == request.user):
        return HttpResponse("Unauthorized or Booking Not Found", status=403)
        
    payment = getattr(booking, 'payment', None)
    payment_method = payment.payment_method if payment else "Not Specified"
    payment_status = payment.get_status_display() if payment else "Pending"
    transaction_id = payment.transaction_id if payment else "N/A"
    
    context = {
        'booking': booking,
        'payment': payment,
        'payment_method': payment_method,
        'payment_status': payment_status,
        'transaction_id': transaction_id,
    }
    return render(request, 'rental/invoice.html', context)

@role_required(['staff', 'admin'])
def update_car_status_view(request, pk, status):
    if status not in ['Available', 'Booked', 'Maintenance', 'Inactive']:
        return HttpResponse("Invalid status", status=400)
    
    car = get_object_or_404(Car, pk=pk)
    car.status = status
    car.save()
    return redirect('car_detail', pk=pk)

@login_required
def booking_detail_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser or booking.user == request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to view this booking.")
    return render(request, 'rental/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser or booking.user == request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to cancel this booking.")
    booking.status = 'cancelled'
    booking.save()
    return redirect('booking_detail', pk=booking.pk)

@login_required
def modify_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser or booking.user == request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to modify this booking.")
    
    if booking.status in ['completed', 'cancelled']:
        return redirect('booking_detail', pk=booking.pk)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            modified_booking = form.save(commit=False)
            delta = modified_booking.return_date - modified_booking.pickup_date
            days = max(delta.days, 1)
            modified_booking.total_price = modified_booking.car.rent_per_day * days
            modified_booking.total_days = days
            modified_booking.save()
            return redirect('booking_detail', pk=modified_booking.pk)
    else:
        form = BookingForm(instance=booking)

    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'rental/booking_modify.html', context)

@login_required
def pickup_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser or booking.user == request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to access this booking.")
    
    from django.utils import timezone
    if booking.status in ['confirmed', 'booked']:
        booking.status = 'picked_up'
        booking.pickup_time = timezone.now()
        booking.save()
        
        # Automatically send Rental Started / Rental Reminder email
        try:
            send_mail(
                subject=f"Rental Started - #BK-{booking.id}",
                message=f"Hi {booking.user.name},\n\nYour rental for the {booking.car.brand} {booking.car.model} has officially started!\n\nImportant Info:\n- Pickup Time: {booking.pickup_time}\n- Expected Return Date: {booking.return_date}\n\nPlease drive safely and adhere to traffic regulations. If you need any assistance, reach out to support@autodrive.com.\n\nBest regards,\nThe AutoDrive Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
            
    elif booking.status == 'picked_up':
        booking.status = 'in_use'
        booking.save()
        
    return redirect('booking_detail', pk=booking.pk)

@login_required
def return_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser or booking.user == request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to access this booking.")
    
    if booking.status != 'in_use':
        return redirect('booking_detail', pk=booking.pk)
        
    if request.method == 'POST':
        damage_report = request.POST.get('damage_report', '').strip()
        from django.utils import timezone
        booking.status = 'returned'
        booking.return_time = timezone.now()
        if damage_report:
            booking.damage_report = damage_report
        booking.save()
        
        # Automatically send Return Confirmation email
        try:
            send_mail(
                subject=f"Vehicle Returned - #BK-{booking.id}",
                message=f"Hi {booking.user.name},\n\nWe have received the return of your rental: {booking.car.brand} {booking.car.model}.\n\nReturn Details:\n- Return Time: {booking.return_time}\n- Damage Report: {booking.damage_report or 'No damage reported'}\n\nOur staff will complete the inspection and finalize the transaction shortly.\n\nBest regards,\nThe AutoDrive Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
            
        return redirect('booking_detail', pk=booking.pk)
        
    return render(request, 'rental/booking_return.html', {'booking': booking})

@role_required(['staff', 'admin'])
def complete_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status != 'returned':
        return redirect('booking_detail', pk=booking.pk)
        
    booking.status = 'completed'
    booking.save()
    
    # Release the car back to available
    car = booking.car
    car.status = 'Available'
    car.save()
    
    return redirect('booking_detail', pk=booking.pk)

@role_required(['staff', 'admin'])
def approve_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status == 'pending':
        booking.status = 'booked'
        booking.save()
        
        # Automatically send Booking Confirmation email
        try:
            send_mail(
                subject=f"Booking Confirmed - #BK-{booking.id}",
                message=f"Hi {booking.user.name},\n\nYour booking request for the {booking.car.brand} {booking.car.model} has been confirmed!\n\nBooking Details:\n- Booking ID: #BK-{booking.id}\n- Vehicle: {booking.car.brand} {booking.car.model}\n- Pickup Date: {booking.pickup_date}\n- Return Date: {booking.return_date}\n- Total Price: ₹{booking.total_price}\n\nThank you for choosing AutoDrive!\n\nBest regards,\nThe AutoDrive Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
            
    return redirect('booking_detail', pk=booking.pk)


@role_required(['admin'])
def admin_users_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        if new_role in ['customer', 'staff', 'admin']:
            user_to_update = get_object_or_404(User, id=user_id)
            user_to_update.role = new_role
            user_to_update.save()
            return redirect('admin_users')

    users = User.objects.all().order_by('name')
    return render(request, 'rental/admin_users.html', {'users': users})


@role_required(['staff', 'admin'])
def admin_bookings_view(request):
    bookings = Booking.objects.all().order_by('-pickup_date')
    return render(request, 'rental/admin_bookings.html', {'bookings': bookings})


@role_required(['admin'])
def admin_payments_view(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        new_status = request.POST.get('status')
        txn_id = request.POST.get('transaction_id', '').strip()
        if new_status in ['Pending', 'Paid', 'Refunded']:
            payment = get_object_or_404(Payment, id=payment_id)
            payment.status = new_status
            if txn_id:
                payment.transaction_id = txn_id
            payment.save()
            return redirect('admin_payments')

    payments = Payment.objects.all().order_by('-payment_date')
    return render(request, 'rental/admin_payments.html', {'payments': payments})


@role_required(['admin'])
def admin_reports_view(request):
    from django.db.models import Sum, Count
    from django.utils import timezone
    
    # 1. Vehicle Report
    total_vehicles = Car.objects.count()
    available_vehicles = Car.objects.filter(status='Available').count()
    booked_vehicles = Car.objects.filter(status='Booked').count()
    
    # 2. Booking Report
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    daily_bookings = Booking.objects.filter(pickup_date=today).count()
    monthly_bookings = Booking.objects.filter(pickup_date__gte=start_of_month).count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    
    # 3. Revenue Report
    start_of_year = today.replace(month=1, day=1)
    
    daily_revenue = Payment.objects.filter(status='Paid', payment_date__date=today).aggregate(total=Sum('amount'))['total'] or 0
    monthly_revenue = Payment.objects.filter(status='Paid', payment_date__gte=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
    yearly_revenue = Payment.objects.filter(status='Paid', payment_date__gte=start_of_year).aggregate(total=Sum('amount'))['total'] or 0
    
    # Fleet utilization metrics
    active_cars = Car.objects.filter(status__in=['Booked', 'Maintenance']).count()
    utilization_rate = round((active_cars / total_vehicles * 100), 1) if total_vehicles > 0 else 0
    
    # Most rented vehicles
    popular_cars = Car.objects.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')[:5]
    
    context = {
        # Vehicle Report
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'booked_vehicles': booked_vehicles,
        
        # Booking Report
        'daily_bookings': daily_bookings,
        'monthly_bookings': monthly_bookings,
        'cancelled_bookings': cancelled_bookings,
        
        # Revenue Report
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,
        
        # General KPIs
        'utilization_rate': utilization_rate,
        'popular_cars': popular_cars,
    }
    return render(request, 'rental/admin_reports.html', context)


@login_required
def collect_payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser or booking.user == request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to access this transaction.")
        
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_price, 'status': 'Pending'}
    )
    
    if payment.status == 'Paid':
        return redirect('booking_detail', pk=booking.pk)
        
    if request.method == 'POST':
        method = request.POST.get('payment_method')
        
        if method not in ['Cash', 'UPI', 'Credit Card', 'Debit Card']:
            return HttpResponse("Invalid payment method", status=400)
            
        import uuid
        payment.status = 'Paid'
        payment.payment_method = method
        payment.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        payment.save()
        return redirect('booking_detail', pk=booking.pk)
        
    return render(request, 'rental/collect_payment.html', {'booking': booking, 'payment': payment})


@login_required
def payment_history_view(request):
    payments = Payment.objects.filter(booking__user=request.user).order_by('-payment_date')
    return render(request, 'rental/payment_history.html', {'payments': payments})


@login_required
def profile_view(request):
    user = request.user
    old_license = user.license_number
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            profile_user = form.save(commit=False)
            if profile_user.license_number != old_license:
                profile_user.is_license_verified = False
            profile_user.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
        
    return render(request, 'rental/profile.html', {'form': form, 'user': user})


@role_required(['staff', 'admin'])
def admin_customers_view(request):
    query = request.GET.get('q', '').strip()
    verification_status = request.GET.get('status', '').strip()
    
    customers = User.objects.filter(role='customer')
    
    if query:
        from django.db.models import Q
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile__icontains=query) |
            Q(license_number__icontains=query)
        )
        
    if verification_status == 'verified':
        customers = customers.filter(is_license_verified=True)
    elif verification_status == 'unverified':
        customers = customers.filter(is_license_verified=False)
        
    customers = customers.order_by('name')
    
    context = {
        'customers': customers,
        'query': query,
        'status_filter': verification_status,
    }
    return render(request, 'rental/admin_customers.html', context)


@role_required(['staff', 'admin'])
def customer_detail_admin_view(request, user_id):
    customer = get_object_or_404(User, id=user_id, role='customer')
    bookings = Booking.objects.filter(user=customer).order_by('-pickup_date')
    
    from django.db.models import Sum
    total_spent = Booking.objects.filter(user=customer, status='completed').aggregate(total=Sum('total_price'))['total'] or 0
    total_bookings = bookings.count()
    
    context = {
        'customer': customer,
        'bookings': bookings,
        'total_spent': total_spent,
        'total_bookings': total_bookings,
    }
    return render(request, 'rental/customer_detail_admin.html', context)


@role_required(['staff', 'admin'])
def verify_license_view(request, user_id):
    customer = get_object_or_404(User, id=user_id, role='customer')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            customer.is_license_verified = True
        elif action == 'unverify':
            customer.is_license_verified = False
        customer.save()
        
    next_url = request.GET.get('next', 'customer_detail_admin')
    if next_url == 'admin_customers':
        return redirect('admin_customers')
    return redirect('customer_detail_admin', user_id=customer.id)


@role_required(['staff', 'admin'])
def admin_maintenance_view(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save()
            if maintenance.status == 'In Progress':
                car = maintenance.car
                car.status = 'Maintenance'
                car.save()
            return redirect('admin_maintenance')
    else:
        form = MaintenanceForm()

    from django.db.models import Sum
    maintenances = Maintenance.objects.all().order_by('-service_date')
    
    total_cost = Maintenance.objects.filter(status='Completed').aggregate(total=Sum('cost'))['total'] or 0
    active_services = Maintenance.objects.filter(status__in=['Scheduled', 'In Progress']).count()
    completed_services = Maintenance.objects.filter(status='Completed').count()

    context = {
        'maintenances': maintenances,
        'form': form,
        'total_cost': total_cost,
        'active_services': active_services,
        'completed_services': completed_services,
    }
    return render(request, 'rental/admin_maintenance.html', context)


@role_required(['staff', 'admin'])
def maintenance_update_view(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        if form.is_valid():
            updated_maintenance = form.save()
            car = updated_maintenance.car
            
            if updated_maintenance.status == 'In Progress':
                car.status = 'Maintenance'
                car.save()
            elif updated_maintenance.status in ['Completed', 'Cancelled']:
                active_maintenances = Maintenance.objects.filter(car=car, status='In Progress').exclude(id=updated_maintenance.id).exists()
                if not active_maintenances:
                    car.status = 'Available'
                    car.save()
                    
            return redirect('admin_maintenance')
    else:
        form = MaintenanceForm(instance=maintenance)
        
    return render(request, 'rental/maintenance_form.html', {'form': form, 'maintenance': maintenance})


@role_required(['staff', 'admin'])
def send_rental_reminder_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    try:
        send_mail(
            subject=f"Upcoming Rental Reminder - #BK-{booking.id}",
            message=f"Hi {booking.user.name},\n\nThis is a friendly reminder for your upcoming rental of the {booking.car.brand} {booking.car.model}.\n\nRental Details:\n- Booking ID: #BK-{booking.id}\n- Vehicle: {booking.car.brand} {booking.car.model}\n- Pickup Date: {booking.pickup_date}\n- Return Date: {booking.return_date}\n- Total Price: ₹{booking.total_price}\n\nPlease ensure you have a valid driving license ready for verification at pickup.\n\nBest regards,\nThe AutoDrive Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        messages.success(request, f"Rental reminder email successfully sent to {booking.user.email}.")
    except Exception as e:
        messages.error(request, f"Failed to send rental reminder email: {str(e)}")
        
    return redirect('booking_detail', pk=booking.pk)


@role_required(['staff', 'admin'])
def send_return_reminder_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    try:
        send_mail(
            subject=f"Rental Return Reminder - #BK-{booking.id}",
            message=f"Hi {booking.user.name},\n\nThis is a friendly reminder that your rental for the {booking.car.brand} {booking.car.model} is scheduled to be returned soon.\n\nReturn Details:\n- Booking ID: #BK-{booking.id}\n- Return Date: {booking.return_date}\n\nPlease ensure you return the vehicle on time with a full tank of fuel. If there are any delays or damages to report, please contact us immediately.\n\nBest regards,\nThe AutoDrive Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        messages.success(request, f"Return reminder email successfully sent to {booking.user.email}.")
    except Exception as e:
        messages.error(request, f"Failed to send return reminder email: {str(e)}")
        
    return redirect('booking_detail', pk=booking.pk)


@role_required(['staff', 'admin'])
def send_payment_reminder_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    try:
        send_mail(
            subject=f"Payment Reminder - #BK-{booking.id}",
            message=f"Hi {booking.user.name},\n\nThis is a reminder that payment is pending for your booking of the {booking.car.brand} {booking.car.model}.\n\nPayment Details:\n- Booking ID: #BK-{booking.id}\n- Amount Due: ₹{booking.total_price}\n\nPlease complete your payment to finalize your booking. If you have already paid, please ignore this email.\n\nBest regards,\nThe AutoDrive Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        messages.success(request, f"Payment reminder email successfully sent to {booking.user.email}.")
    except Exception as e:
        messages.error(request, f"Failed to send payment reminder: {str(e)}")
        
    return redirect('booking_detail', pk=booking.pk)


import random
from django.utils import timezone
from datetime import timedelta

def password_reset_otp_request_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            # Generate a 6-digit numeric OTP
            otp_code = str(random.randint(100000, 999999))
            
            # Save variables to the session dictionary
            request.session['reset_otp'] = otp_code
            request.session['reset_email'] = email
            request.session['reset_otp_expiry'] = (timezone.now() + timedelta(minutes=10)).isoformat()
            request.session['otp_verified'] = False
            
            # Send real email via SMTP settings
            try:
                send_mail(
                    subject="AutoDrive Password Reset OTP",
                    message=f"Hello,\n\nYou have requested to reset your password for AutoDrive.\n\nYour 6-digit verification code is: {otp_code}\n\nThis code is valid for 10 minutes. If you did not make this request, you can safely ignore this email.\n\nBest regards,\nThe AutoDrive Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f"A verification code has been successfully sent to {email}.")
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
                return render(request, 'rental/password_reset_form.html')
                
            return redirect('password_reset_verify')
        else:
            messages.error(request, "No registered user found with that email address.")
            
    return render(request, 'rental/password_reset_form.html')


def password_reset_otp_verify_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if 'reset_otp' not in request.session or 'reset_email' not in request.session:
        return redirect('password_reset')
        
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        session_otp = request.session.get('reset_otp')
        expiry_str = request.session.get('reset_otp_expiry')
        
        # Validate expiration
        is_expired = True
        if expiry_str:
            expiry_time = timezone.datetime.fromisoformat(expiry_str)
            if timezone.now() < expiry_time:
                is_expired = False
                
        if entered_otp == session_otp and not is_expired:
            request.session['otp_verified'] = True
            return redirect('password_reset_change')
        else:
            messages.error(request, "Invalid or expired verification code. Please check and try again.")
            
    return render(request, 'rental/password_reset_otp_verify.html')


def password_reset_otp_change_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if not request.session.get('otp_verified') or 'reset_email' not in request.session:
        return redirect('password_reset')
        
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not password or len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('reset_email')
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(password)
                user.save()
                
                # Clean up session
                request.session.pop('reset_otp', None)
                request.session.pop('reset_email', None)
                request.session.pop('reset_otp_expiry', None)
                request.session.pop('otp_verified', None)
                
                messages.success(request, "Your password has been successfully updated. Please login with your new password.")
                return redirect('login')
            else:
                messages.error(request, "User not found.")
                
    return render(request, 'rental/password_reset_otp_change.html')


@login_required
def submit_review_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status not in ['returned', 'completed']:
        messages.error(request, "You can only write a review after the vehicle has been returned.")
        return redirect('booking_detail', pk=booking.id)
        
    if hasattr(booking, 'review'):
        messages.error(request, "You have already submitted a review for this booking.")
        return redirect('booking_detail', pk=booking.id)
        
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (TypeError, ValueError):
            messages.error(request, "Please select a rating between 1 and 5 stars.")
            return redirect('booking_detail', pk=booking.id)
            
        if not comment:
            messages.error(request, "Please enter a comment for your review.")
            return redirect('booking_detail', pk=booking.id)
            
        Review.objects.create(
            booking=booking,
            user=request.user,
            car=booking.car,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Thank you! Your review has been submitted successfully.")
        
    return redirect('booking_detail', pk=booking.id)

