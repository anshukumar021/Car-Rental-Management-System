from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import User, Car, Category, Booking, Maintenance

User = get_user_model()

class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'mobile', 'license_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.label}'
            })

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email Address',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password'
    }))

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.label}'
            })

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('name', 'brand', 'model', 'category', 'year', 'fuel_type', 'transmission', 'seating_capacity', 'rent_per_day', 'image', 'status')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'image':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter {field.label}'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control'
                })

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('car', 'pickup_date', 'return_date')
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'return_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.db.models import Q
        current_car_id = self.instance.car_id if (self.instance and self.instance.pk) else None
        if current_car_id:
            self.fields['car'].queryset = Car.objects.filter(Q(status='Available') | Q(id=current_car_id))
        else:
            self.fields['car'].queryset = Car.objects.filter(status='Available')
        self.fields['car'].widget.attrs.update({'class': 'form-select'})
        for field_name in ['pickup_date', 'return_date']:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'mobile', 'license_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.label}'
            })


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ('car', 'service_date', 'service_type', 'cost', 'status', 'notes')
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter service details...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['car'].queryset = Car.objects.all().order_by('brand', 'model')
        self.fields['car'].widget.attrs.update({'class': 'form-select'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        for field_name in ['service_type', 'cost']:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {self.fields[field_name].label}'
            })

