from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Car, Booking, Category, Review

class UserAdmin(BaseUserAdmin):
    """
    Configure Django Admin interface for custom User model.
    """
    ordering = ('email',)
    list_display = ('email', 'name', 'mobile', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'name', 'mobile', 'license_number')
    
    # Configure edit form field groupings
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'mobile', 'license_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Configure add form field groupings
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'mobile', 'license_number', 'role', 'password'),
        }),
    )

admin.site.register(User, UserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'model', 'category', 'year', 'fuel_type', 'transmission', 'seating_capacity', 'rent_per_day', 'status')
    list_filter = ('brand', 'category', 'fuel_type', 'transmission', 'status')
    search_fields = ('name', 'brand', 'model')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car', 'pickup_date', 'return_date', 'status', 'total_price')
    list_filter = ('status', 'pickup_date')
    search_fields = ('user__email', 'user__name', 'car__brand', 'car__model')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'user', 'car', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__name', 'user__email', 'car__brand', 'car__model', 'comment')
