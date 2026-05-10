from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Customer
import re
from datetime import date


class RegisterForm(forms.ModelForm):

    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Full Name'
    }))

    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))

    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }

    # 🔐 PASSWORD VALIDATION
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm:

            if password != confirm:
                raise forms.ValidationError("Passwords do not match")

            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters")

            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Password must contain an uppercase letter")

            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Password must contain a lowercase letter")

            if not re.search(r'\d', password):
                raise forms.ValidationError("Password must contain a number")

            # Django built-in validation
            validate_password(password)

        return cleaned_data

    # 👤 USERNAME VALIDATION
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters")

        if not username.isalnum():
            raise forms.ValidationError("Username must be alphanumeric")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken")

        return username

    # 📧 EMAIL VALIDATION
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")

        return email

    # 📱 PHONE VALIDATION
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone.isdigit():
            raise forms.ValidationError("Phone must contain only digits")

        if len(phone) != 10:
            raise forms.ValidationError("Phone must be exactly 10 digits")

        if not phone.startswith(('6', '7', '8', '9')):
            raise forms.ValidationError("Enter a valid Indian phone number")

        return phone

    # 🎂 AGE VALIDATION (18+)
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')

        if not dob:
            raise forms.ValidationError("Date of birth is required")

        today = date.today()

        # ✅ Accurate age calculation
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if dob > today:
            raise forms.ValidationError("Date of birth cannot be in the future")

        if age < 18:
            raise forms.ValidationError("You must be at least 18 years old")

        if age > 100:
            raise forms.ValidationError("Enter a valid age")

        return dob

    # 💾 SAVE USER + UPDATE CUSTOMER
    def save(self, commit=True):
     user = super().save(commit=False)
     user.set_password(self.cleaned_data['password'])

     if commit:
        user.save()

        # ✅ SAFE: get or create customer
        customer, created = Customer.objects.get_or_create(user=user)

        customer.full_name = self.cleaned_data['full_name']
        customer.phone = self.cleaned_data['phone']
        customer.date_of_birth = self.cleaned_data['date_of_birth']
        customer.save()

     return user