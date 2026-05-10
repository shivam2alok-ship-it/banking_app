from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Sum
from decimal import Decimal
import random

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Case, When, F, DecimalField
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from datetime import datetime
from .form import RegisterForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import SupportRequest
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import Customer, Transaction


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # optional next redirect
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'dashboard')

        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib import messages
from .form import RegisterForm
from .models import Customer
import random


def register_view(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            # SAVE USER
            user = form.save(commit=False)

            # GENERATE UNIQUE ACCOUNT NUMBER
            account_number = str(random.randint(1000000000, 9999999999))

            while Customer.objects.filter(account_number=account_number).exists():
                account_number = str(random.randint(1000000000, 9999999999))

            # SAVE USER
            user.save()

            # CREATE / UPDATE CUSTOMER
            customer, created = Customer.objects.get_or_create(user=user)

            customer.account_number = account_number
            customer.full_name = form.cleaned_data['full_name']
            customer.phone = form.cleaned_data['phone']
            customer.date_of_birth = form.cleaned_data['date_of_birth']

            customer.save()

            messages.success(request, "Account created successfully")

            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {
        'form': form
    })

def send_transaction_email(user, subject, message):
    if user.email:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=True
        )



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from core.models import Transaction, Customer
import json
import random


def generate_account_number():
    while True:
        acc = str(random.randint(1000000000, 9999999999))
        if not Customer.objects.filter(account_number=acc).exists():
            return acc


@login_required
def dashboard(request):
    # ✅ SAFE WAY (NO ERROR EVER)
    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={'account_number': generate_account_number()}
    )

    if not customer.transaction_pin:
        return redirect('set_pin')

    all_transactions = Transaction.objects.filter(
        Q(sender=customer) | Q(receiver=customer)
    )

    transactions = all_transactions.order_by('-timestamp')[:5]

    totals = all_transactions.aggregate(
        total_credit=Sum('amount', filter=Q(receiver=customer)),
        total_debit=Sum('amount', filter=Q(sender=customer)),
    )

    total_credit = totals['total_credit'] or 0
    total_debit = totals['total_debit'] or 0

    monthly_data = (
        all_transactions
        .annotate(month=TruncMonth('timestamp'))
        .values('month')
        .annotate(
            credit=Sum('amount', filter=Q(receiver=customer)),
            debit=Sum('amount', filter=Q(sender=customer)),
        )
        .order_by('month')
    )

    months = [d['month'].strftime('%b') for d in monthly_data if d['month']]
    credits = [float(d['credit'] or 0) for d in monthly_data]
    debits = [float(d['debit'] or 0) for d in monthly_data]

    if not months:
        months = ["No Data"]
        credits = [0]
        debits = [0]

    return render(request, 'dashboard.html', {
        'customer': customer,
        'transactions': transactions,
        'total_credit': total_credit,
        'total_debit': total_debit,
        'transaction_count': all_transactions.count(),
        'profile_completion': customer.profile_completion(),
        'months': json.dumps(months),
        'credits': json.dumps(credits),
        'debits': json.dumps(debits),
    })
    
        
from django.contrib import messages
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import Customer, Transaction
import uuid

@login_required
def deposit_view(request):
    customer = request.user.customer

    if request.method == "POST":
        amount = request.POST.get("amount")

        #  VALIDATION 1: Empty / invalid input
        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "Invalid amount entered")
            return redirect("deposit")

        #  VALIDATION 2: Minimum deposit rule
        if amount <= 0:
            messages.error(request, "Amount must be greater than 0")
            return redirect("deposit")

        #  OPTIONAL RULE (real banking style)
        if amount > 100000:
            messages.error(request, "Deposit limit exceeded (₹1,00,000 per transaction)")
            return redirect("deposit")

        #  UPDATE BALANCE
        customer.balance += amount
        customer.save()

        #  CREATE TRANSACTION
        Transaction.objects.create(
            receiver=customer,
            amount=amount,
            transaction_type="DEPOSIT",
            reference_id=str(uuid.uuid4()),
            status="SUCCESS"
        )

        messages.success(request, f"₹{amount} deposited successfully")
        return redirect("dashboard")

    return render(request, "deposit.html", {"customer": customer})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import Transaction

@login_required
def withdraw(request):
    customer = request.user.customer

    if request.method == "POST":
        amount = Decimal(request.POST.get('amount', 0))

        # BASIC VALIDATION
        if amount <= 0:
            messages.error(request, "Enter a valid amount")
            return redirect('withdraw')

        # MINIMUM BALANCE RULE (IMPORTANT)
        if customer.balance - amount < 100:
            messages.error(
                request,
                "Withdrawal denied. Minimum balance of ₹100 must be maintained."
            )
            return redirect('withdraw')

        # PROCESS WITHDRAWAL
        customer.balance -= amount
        customer.save()

        Transaction.objects.create(
            sender=customer,
            amount=amount,
            transaction_type="WITHDRAW"
        )

        messages.success(request, f"₹{amount} withdrawn successfully")
        return redirect('dashboard')

    return render(request, 'withdraw.html', {
        'customer': customer
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import timedelta

from .models import Customer, Transaction

from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Customer, Transaction


@login_required
def transfer_view(request):
    sender = request.user.customer

    if request.method == "POST":
        acc_no = request.POST.get('account_number', '').strip()
        amount_raw = request.POST.get('amount')
        pin = request.POST.get('pin')

        # -------------------------
        # 0. PIN VALIDATION
        # -------------------------
        if not pin:
            messages.error(request, "PIN is required")
            return redirect('transfer')

        if not sender.check_pin(pin):
            messages.error(request, "Invalid PIN")
            return redirect('transfer')

        # -------------------------
        # 1. VALIDATE AMOUNT
        # -------------------------
        try:
            amount = Decimal(amount_raw)
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount")
            return redirect('transfer')

        if amount <= 0:
            messages.error(request, "Amount must be greater than zero")
            return redirect('transfer')

        # -------------------------
        # 2. FIND RECEIVER
        # -------------------------
        try:
            receiver = Customer.objects.get(account_number=acc_no)
        except Customer.DoesNotExist:
            messages.error(request, "Account not found")
            return redirect('transfer')

        # -------------------------
        # 3. SELF TRANSFER CHECK
        # -------------------------
        if receiver == sender:
            messages.error(request, "You cannot transfer to your own account")
            return redirect('transfer')

        # -------------------------
        # 4. BALANCE CHECK
        # -------------------------
        if sender.balance < amount:
            messages.error(request, "Insufficient balance")
            return redirect('transfer')

        # -------------------------
        # 5. DUPLICATE PREVENTION
        # -------------------------
        recent_time = timezone.now() - timedelta(seconds=10)

        duplicate = Transaction.objects.filter(
            sender=sender,
            receiver=receiver,
            amount=amount,
            transaction_type="TRANSFER",
            timestamp__gte=recent_time
        ).exists()

        if duplicate:
            messages.error(request, "Duplicate transfer detected. Please wait.")
            return redirect('transfer')

        # -------------------------
        # 6. TRANSACTION EXECUTION
        # -------------------------
        with transaction.atomic():
            sender.balance -= amount
            receiver.balance += amount

            sender.save()
            receiver.save()

            Transaction.objects.create(
                sender=sender,
                receiver=receiver,
                amount=amount,
                transaction_type="TRANSFER",
                status="SUCCESS",
                reference_id=f"TXN{timezone.now().timestamp()}"
            )

        # -------------------------
        # 7. SUCCESS
        # -------------------------
        messages.success(request, f"₹{amount} sent successfully")
        return redirect('dashboard')

    return render(request, 'transfer.html', {
        'customer': sender
    })
@login_required

def transaction_history(request):
    customer = request.user.customer

    transactions = Transaction.objects.filter(
        Q(sender=customer) | Q(receiver=customer)
    )

    # FILTERS
    tx_type = request.GET.get('type')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    search = request.GET.get('search')

    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)

    if start_date:
        transactions = transactions.filter(timestamp__date__gte=start_date)

    if end_date:
        transactions = transactions.filter(timestamp__date__lte=end_date)

    if search:
        transactions = transactions.filter(
            Q(sender__account_number__icontains=search) |
            Q(receiver__account_number__icontains=search)
        )

    transactions = transactions.order_by('-timestamp')

    return render(request, 'transactions.html', {
        'transactions': transactions
    })
    
    
@login_required

def download_statement(request):
    customer = request.user.customer

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="statement.pdf"'

    doc = SimpleDocTemplate(response)
    elements = []

    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Bank Statement", styles['Title']))
    elements.append(Paragraph(f"Name: {request.user.username}", styles['Normal']))
    elements.append(Paragraph(f"Account: {customer.account_number}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))

    # Transactions
    transactions = Transaction.objects.filter(
        Q(sender=customer) | Q(receiver=customer)
    ).order_by('-timestamp')

    data = [["Type", "Details", "Amount", "Date"]]

    for t in transactions:
        if t.transaction_type == "TRANSFER":
            if t.sender == customer:
                detail = f"Sent to {t.receiver.account_number}"
                amount = f"-₹{t.amount}"
            else:
                detail = f"Received from {t.sender.account_number}"
                amount = f"+₹{t.amount}"
        elif t.transaction_type == "DEPOSIT":
            detail = "Deposit"
            amount = f"+₹{t.amount}"
        else:
            detail = "Withdraw"
            amount = f"-₹{t.amount}"

        data.append([
            t.transaction_type,
            detail,
            amount,
            t.timestamp.strftime("%d-%m-%Y %H:%M")
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)

    doc.build(elements)
    return response



from .models import FixedDeposit
from datetime import datetime


@login_required
def profile_view(request):

    customer = getattr(request.user, 'customer', None)

    if not customer:
        messages.error(request, "Customer not found")
        return redirect('home')

    # ✅ FETCH USER FDs
    fds = FixedDeposit.objects.filter(
        customer=customer
    ).order_by('-created_at')

    if request.method == "POST":

        customer.full_name = request.POST.get('full_name')
        customer.phone = request.POST.get('phone')

        dob = request.POST.get('date_of_birth')

        if dob:
            try:
                customer.date_of_birth = datetime.strptime(
                    dob,
                    "%Y-%m-%d"
                ).date()

            except:
                messages.error(request, "Invalid date format")

        customer.pan_number = request.POST.get('pan_number')
        customer.aadhaar_number = request.POST.get('aadhaar_number')

        # ✅ Image upload
        if request.FILES.get('profile_picture'):
            customer.profile_picture = request.FILES['profile_picture']

        customer.save()

        messages.success(request, "Profile updated successfully")

        return redirect('profile')

    return render(request, 'profile.html', {

        'customer': customer,

        'completion_percentage': customer.profile_completion(),

        # ✅ SEND FDs TO TEMPLATE
        'fds': fds,
    })
    
    
from django.shortcuts import render
from django.contrib import messages

def support_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # For now just show success (you can save later)
        messages.success(request, "Your query has been submitted!")

    return render(request, 'support.html')


from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import FixedDeposit, SupportRequest


@login_required
def apply_fd(request):

    customer = request.user.customer

    if request.method == "POST":

        amount = request.POST.get('amount')
        duration = request.POST.get('duration')

        # ✅ Empty validation
        if not amount or not duration:
            messages.error(request, "All fields are required")
            return redirect('apply_fd')

        # ✅ Convert properly
        amount = Decimal(amount)
        duration = int(duration)

        # ✅ Minimum FD amount
        if amount < Decimal('1000'):
            messages.error(request, "Minimum FD amount is ₹1000")
            return redirect('apply_fd')

        # ✅ Balance check
        if amount > customer.balance:
            messages.error(request, "Insufficient balance")
            return redirect('apply_fd')

        # ✅ Interest logic
        if duration >= 24:
            rate = Decimal('7.50')

        elif duration >= 12:
            rate = Decimal('6.80')

        else:
            rate = Decimal('6.00')

        # ✅ Deduct balance
        customer.balance -= amount
        customer.save()

        # ✅ Create FD
        FixedDeposit.objects.create(
            customer=customer,
            amount=amount,
            duration=duration,
            interest_rate=rate
        )

        messages.success(request, "Fixed Deposit created successfully")

        return redirect('apply_fd')

    return render(request, 'apply_fd.html')


def create_request(request):
    return render(request, 'create_request.html')


def my_requests(request):
    customer = request.user.customer

    requests = SupportRequest.objects.filter(
        customer=customer
    ).order_by('-created_at')

    return render(request, 'my_requests.html', {
        'requests': requests
    })


def home(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'home.html')


@login_required
def set_pin(request):

    customer = request.user.customer

    # ✅ If PIN already exists
    if customer.transaction_pin:
        messages.info(request, "PIN already set")
        return redirect('dashboard')

    if request.method == 'POST':

        pin = request.POST.get('pin')
        confirm_pin = request.POST.get('confirm_pin')

        # ✅ Empty fields
        if not pin or not confirm_pin:
            return render(request, 'set_pin.html', {
                'error': 'All fields are required'
            })

        # ✅ PIN validation
        if not pin.isdigit() or len(pin) != 4:
            return render(request, 'set_pin.html', {
                'error': 'PIN must be exactly 4 digits'
            })

        # ✅ Match validation
        if pin != confirm_pin:
            return render(request, 'set_pin.html', {
                'error': 'PINs do not match'
            })

        # ✅ Weak PIN prevention
        weak_pins = ['0000', '1111', '1234', '2222', '4321']

        if pin in weak_pins:
            return render(request, 'set_pin.html', {
                'error': 'Choose a stronger PIN'
            })

        # ✅ Save hashed PIN
        customer.set_pin(pin)

        messages.success(request, "PIN set successfully")

        return redirect('dashboard')

    return render(request, 'set_pin.html')

def create_request(request):
    return render(request, 'create_request.html')

def my_requests(request):
    return render(request, 'my_requests.html')

def my_requests(request):
    customer = request.user.customer
    requests = SupportRequest.objects.filter(customer=customer).order_by('-created_at')

    return render(request, 'my_requests.html', {'requests': requests})

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def set_pin(request):
    customer = request.user.customer

    #  If PIN already exists → skip
    #  If PIN already exists → skip
    if customer.transaction_pin:
        messages.info(request, "PIN already set")
        return redirect('dashboard')

    if request.method == 'POST':
        pin = request.POST.get('pin')
        confirm_pin = request.POST.get('confirm_pin')

        #  Required check
        if not pin or not confirm_pin:
            return render(request, 'set_pin.html', {
                'error': 'All fields are required'
            })

        #  Format validation
        if not pin.isdigit() or len(pin) != 4:
            return render(request, 'set_pin.html', {
                'error': 'PIN must be exactly 4 digits'
            })

        #  Match check
        if pin != confirm_pin:
            return render(request, 'set_pin.html', {
                'error': 'PINs do not match'
            })

        #  Weak PIN prevention
        weak_pins = ['0000', '1111', '1234', '2222', '4321']
        if pin in weak_pins:
            return render(request, 'set_pin.html', {
                'error': 'Choose a stronger PIN'
            })

        # Save securely
        customer.set_pin(pin)

        messages.success(request, "PIN set successfully")
        return redirect('dashboard')

    return render(request, 'set_pin.html')