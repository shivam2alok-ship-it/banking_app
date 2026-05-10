from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import post_save
from django.dispatch import receiver
import re
import uuid


import random

def generate_account_number():
    while True:
        acc_no = str(random.randint(1000000000, 9999999999))
        if not Customer.objects.filter(account_number=acc_no).exists():
            return acc_no


# 👤 CUSTOMER MODEL
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    pan_number = models.CharField(max_length=10, null=True, blank=True)
    aadhaar_number = models.CharField(max_length=12, null=True, blank=True)

    account_status = models.CharField(
        max_length=10,
        choices=[
            ('ACTIVE', 'Active'),
            ('FROZEN', 'Frozen'),
        ],
        default='ACTIVE'
    )
    
   # KYC STATUS
    kyc_status = models.CharField(
    max_length=10,
    choices=[
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ],
    default='PENDING'
)

    # 🔐 TRANSACTION PIN (hashed)
    transaction_pin = models.CharField(max_length=128, null=True, blank=True)

    # 🔑 SET PIN
    def set_pin(self, raw_pin):
        self.transaction_pin = make_password(raw_pin)
        self.save()

    # 🔑 VERIFY PIN
    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.transaction_pin)

    def __str__(self):
        return self.user.username
        
   
    # 📊 PROFILE COMPLETION
    def profile_completion(self):
        fields = [
            self.full_name,
            self.phone,
            self.date_of_birth,
            self.pan_number,
            self.aadhaar_number,
            self.profile_picture,
        ]
        filled = sum(1 for field in fields if field)
        return int((filled / len(fields)) * 100)

    # ✅ VALIDATIONS
    def clean(self):
        if self.pan_number:
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', self.pan_number):
                raise ValidationError("Invalid PAN format")

        if self.aadhaar_number:
            if not re.match(r'^[0-9]{12}$', self.aadhaar_number):
                raise ValidationError("Invalid Aadhaar number")
    def save(self, *args, **kwargs):
        if not self.account_number:
           self.account_number = generate_account_number()
        super().save(*args, **kwargs)
# ⚡ AUTO CREATE CUSTOMER WHEN USER IS CREATED


# 💸 TRANSACTION MODEL
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('TRANSFER', 'Transfer'),
    )

    sender = models.ForeignKey(
        Customer,
        related_name='sent_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    receiver = models.ForeignKey(
        Customer,
        related_name='received_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)

    reference_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)

    status = models.CharField(
        max_length=10,
        choices=[
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
            ('PENDING', 'Pending'),
        ],
        default='SUCCESS'
    )

    # 🔐 Fraud tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sender', 'timestamp']),
            models.Index(fields=['receiver', 'timestamp']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - ₹{self.amount}"


# 🛠 SUPPORT SYSTEM
class SupportRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    subject = models.CharField(max_length=100)
    message = models.TextField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.subject}"


# 💼 FIXED DEPOSIT MODEL
from django.db import models
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta


from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal


class FixedDeposit(models.Model):

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('MATURED', 'Matured'),
        ('CLOSED', 'Closed'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    duration = models.IntegerField(
        help_text="Duration in months"
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('6.50')
    )

    maturity_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    maturity_date = models.DateField(
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):

        # ✅ Convert months into years
        years = Decimal(self.duration) / Decimal('12')

        # ✅ Simple Interest Formula
        # SI = (P × R × T) / 100

        interest = (
            self.amount *
            self.interest_rate *
            years
        ) / Decimal('100')

        self.maturity_amount = self.amount + interest

        # ✅ Set maturity date
        if not self.maturity_date:
            self.maturity_date = (
                timezone.now().date()
                + relativedelta(months=self.duration)
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.user.username} - FD ₹{self.amount}"