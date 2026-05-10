from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

from django.contrib.auth.models import User

from core.models import (
    Customer,
    Transaction,
    SupportRequest,
    FixedDeposit
)


# =========================================
# CHECK SUPERUSER
# =========================================

def superuser_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('admin_login')

        if not request.user.is_superuser:
            logout(request)
            return redirect('admin_login')

        return view_func(request, *args, **kwargs)

    return wrapper


# =========================================
# ADMIN LOGIN
# =========================================

def admin_login(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_superuser:

            login(request, user)

            messages.success(
                request,
                "Welcome Admin"
            )

            return redirect('admin_dashboard')

        else:

            messages.error(
                request,
                "Only Admin can login."
            )

    return render(
        request,
        'admin_panel/admin_login.html'
    )


# =========================================
# ADMIN DASHBOARD
# =========================================

@superuser_required
def admin_dashboard(request):

    # ================= USERS =================

    total_users = Customer.objects.count()

    active_users = Customer.objects.filter(
        account_status='ACTIVE'
    ).count()

    frozen_users = Customer.objects.filter(
        account_status='FROZEN'
    ).count()

    recent_users = Customer.objects.select_related(
        'user'
    ).order_by('-id')[:5]



    # ================= MONEY =================

    total_balance = Customer.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0


    total_deposits = Transaction.objects.filter(
        transaction_type='DEPOSIT'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0


    total_withdrawals = Transaction.objects.filter(
        transaction_type='WITHDRAW'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0



    # ================= TRANSACTIONS =================

    total_transactions = Transaction.objects.count()

    successful_transactions = Transaction.objects.filter(
        status='SUCCESS'
    ).count()

    failed_transactions = Transaction.objects.filter(
        status='FAILED'
    ).count()

    recent_transactions = Transaction.objects.select_related(
        'sender',
        'receiver'
    ).order_by('-timestamp')[:10]



    # ================= TODAY ACTIVITY =================

    today = timezone.now().date()

    today_transactions = Transaction.objects.filter(
        timestamp__date=today
    ).count()



    # ================= FIXED DEPOSITS =================

    active_fd = FixedDeposit.objects.filter(
        status='ACTIVE'
    ).count()

    total_fd_amount = FixedDeposit.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0



    # ================= SUPPORT =================

    pending_support = SupportRequest.objects.filter(
        status='PENDING'
    ).count()

    resolved_support = SupportRequest.objects.filter(
        status='RESOLVED'
    ).count()



    context = {

        'total_users': total_users,
        'active_users': active_users,
        'frozen_users': frozen_users,
        'recent_users': recent_users,

        'total_balance': total_balance,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,

        'total_transactions': total_transactions,
        'successful_transactions': successful_transactions,
        'failed_transactions': failed_transactions,
        'recent_transactions': recent_transactions,

        'today_transactions': today_transactions,

        'active_fd': active_fd,
        'total_fd_amount': total_fd_amount,

        'pending_support': pending_support,
        'resolved_support': resolved_support,

        'admin_name': request.user.username,
    }

    return render(
        request,
        'admin_panel/dashboard.html',
        context
    )


# =========================================
# MANAGE USERS
# =========================================

@superuser_required
def manage_users(request):

    users = Customer.objects.select_related(
        'user'
    ).order_by('-id')

    return render(
        request,
        'admin_panel/manage_users.html',
        {
            'users': users
        }
    )


# =========================================
# USER DETAILS
# =========================================

@superuser_required
def user_detail(request, user_id):

    customer = get_object_or_404(
        Customer,
        id=user_id
    )

    transactions = Transaction.objects.filter(
        sender=customer
    ).order_by('-timestamp')

    return render(
        request,
        'admin_panel/user_detail.html',
        {
            'customer': customer,
            'transactions': transactions
        }
    )


# =========================================
# FREEZE ACCOUNT
# =========================================

@superuser_required
def freeze_account(request, user_id):

    customer = get_object_or_404(
        Customer,
        id=user_id
    )

    customer.account_status = 'FROZEN'
    customer.save()

    messages.warning(
        request,
        "Account Frozen Successfully"
    )

    return redirect('manage_users')


# =========================================
# ACTIVATE ACCOUNT
# =========================================

@superuser_required
def activate_account(request, user_id):

    customer = get_object_or_404(
        Customer,
        id=user_id
    )

    customer.account_status = 'ACTIVE'
    customer.save()

    messages.success(
        request,
        "Account Activated Successfully"
    )

    return redirect('manage_users')


# =========================================
# ALL TRANSACTIONS
# =========================================

@superuser_required
def all_transactions(request):

    transactions = Transaction.objects.select_related(
        'sender',
        'receiver'
    ).order_by('-timestamp')

    return render(
        request,
        'admin_panel/transactions.html',
        {
            'transactions': transactions
        }
    )


# =========================================
# SUPPORT REQUESTS
# =========================================

@superuser_required
def support_requests(request):

    requests = SupportRequest.objects.select_related(
        'customer'
    ).order_by('-created_at')

    return render(
        request,
        'admin_panel/support_requests.html',
        {
            'requests': requests
        }
    )


# =========================================
# FIXED DEPOSITS
# =========================================

@superuser_required
def fixed_deposits(request):

    deposits = FixedDeposit.objects.select_related(
        'customer'
    ).order_by('-created_at')

    return render(
        request,
        'admin_panel/fixed_deposits.html',
        {
            'deposits': deposits
        }
    )


# =========================================
# SECURITY PANEL
# =========================================

@superuser_required
def security_panel(request):

    suspicious_transactions = Transaction.objects.filter(
        amount__gte=50000
    ).order_by('-timestamp')

    return render(
        request,
        'admin_panel/security_panel.html',
        {
            'transactions': suspicious_transactions
        }
    )


# =========================================
# ADMIN LOGOUT
# =========================================

def admin_logout(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully"
    )

    return redirect('admin_login')
# =========================================
# ADD USER
# =========================================

@superuser_required
def add_user(request):

    recent_users = Customer.objects.select_related(
        'user'
    ).order_by('-id')[:5]

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')

        account_type = request.POST.get('account_type')
        balance = request.POST.get('balance')

        # Check username exists

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect('add_user')

        # Create Django User

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Generate account number

        import random

        account_number = str(
            random.randint(1000000000, 9999999999)
        )

        # Create Customer

        Customer.objects.create(
            user=user,
            phone=phone,
            account_number=account_number,
            account_type=account_type,
            balance=balance,
            account_status='ACTIVE'
        )

        messages.success(
            request,
            "Customer account created successfully"
        )

        return redirect('add_user')

    return render(
        request,
        'admin_panel/add_user.html',
        {
            'recent_users': recent_users
        }
    )
    
from django.core.paginator import Paginator


# =========================================
# FREEZE ACCOUNTS DASHBOARD
# =========================================

@superuser_required
def freeze_accounts(request):

    # =====================================
    # FILTER STATUS
    # =====================================

    status = request.GET.get('status', 'ALL')


    # =====================================
    # GET CUSTOMERS
    # =====================================

    customers = Customer.objects.select_related(
        'user'
    ).order_by('-id')


    # =====================================
    # APPLY FILTERS
    # =====================================

    if status == 'ACTIVE':

        customers = customers.filter(
            account_status='ACTIVE'
        )

    elif status == 'FROZEN':

        customers = customers.filter(
            account_status='FROZEN'
        )


    # =====================================
    # PAGINATION
    # =====================================

    paginator = Paginator(customers, 10)

    page_number = request.GET.get('page')

    customers = paginator.get_page(page_number)


    # =====================================
    # STATS
    # =====================================

    total_users = Customer.objects.count()

    active_users = Customer.objects.filter(
        account_status='ACTIVE'
    ).count()

    frozen_users = Customer.objects.filter(
        account_status='FROZEN'
    ).count()


    # =====================================
    # CONTEXT
    # =====================================

    context = {

        'customers': customers,

        'current_status': status,

        'total_users': total_users,

        'active_users': active_users,

        'frozen_users': frozen_users,
    }


    return render(
        request,
        'admin_panel/freeze_accounts.html',
        context
    )
# =========================================
# VERIFY KYC PAGE
# =========================================

@superuser_required
def verify_kyc(request):

    status = request.GET.get('status', 'PENDING')

    customers = Customer.objects.select_related(
        'user'
    ).order_by('-created_at')

    # FILTERS

    if status == 'PENDING':

        customers = customers.filter(
            kyc_status='PENDING'
        )

    elif status == 'VERIFIED':

        customers = customers.filter(
            kyc_status='VERIFIED'
        )

    elif status == 'REJECTED':

        customers = customers.filter(
            kyc_status='REJECTED'
        )

    # COUNTS

    pending_count = Customer.objects.filter(
        kyc_status='PENDING'
    ).count()

    verified_count = Customer.objects.filter(
        kyc_status='VERIFIED'
    ).count()

    rejected_count = Customer.objects.filter(
        kyc_status='REJECTED'
    ).count()

    context = {

        'customers': customers,

        'pending_count': pending_count,
        'verified_count': verified_count,
        'rejected_count': rejected_count,

        'current_status': status,
    }

    return render(
        request,
        'admin_panel/verify_kyc.html',
        context
    )
    
# =========================================
# APPROVE KYC
# =========================================

@superuser_required
def approve_kyc(request, user_id):

    customer = get_object_or_404(
        Customer,
        id=user_id
    )

    customer.kyc_status = 'VERIFIED'

    customer.save()

    messages.success(
        request,
        "KYC Approved Successfully"
    )

    return redirect('verify_kyc')

# =========================================
# REJECT KYC
# =========================================

@superuser_required
def reject_kyc(request, user_id):

    customer = get_object_or_404(
        Customer,
        id=user_id
    )

    customer.kyc_status = 'REJECTED'

    customer.save()

    messages.warning(
        request,
        "KYC Rejected"
    )

    return redirect('verify_kyc')
    
    
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
import csv

from core.models import Customer, Transaction, SupportRequest


@staff_member_required
def reports_view(request):

    today = timezone.now().date()

    total_users = Customer.objects.count()

    total_balance = Customer.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0

    total_transactions = Transaction.objects.count()

    today_transactions = Transaction.objects.filter(
        timestamp__date=today
    ).count()

    total_deposits = Transaction.objects.filter(
        transaction_type='DEPOSIT'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_withdrawals = Transaction.objects.filter(
        transaction_type='WITHDRAW'
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending_support = SupportRequest.objects.filter(
        status='PENDING'
    ).count()

    resolved_support = SupportRequest.objects.filter(
        status='RESOLVED'
    ).count()

    recent_transactions = Transaction.objects.select_related(
        'sender',
        'receiver'
    ).order_by('-timestamp')[:10]

    suspicious_transactions = Transaction.objects.filter(
        amount__gte=50000
    ).order_by('-timestamp')[:5]

    context = {
        'total_users': total_users,
        'total_balance': total_balance,
        'total_transactions': total_transactions,
        'today_transactions': today_transactions,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'pending_support': pending_support,
        'resolved_support': resolved_support,
        'recent_transactions': recent_transactions,
        'suspicious_transactions': suspicious_transactions,
    }

    return render(request, 'admin_panel/reports.html', context)


@staff_member_required
def export_transactions_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Sender',
        'Receiver',
        'Amount',
        'Type',
        'Status',
        'Timestamp'
    ])

    transactions = Transaction.objects.all().order_by('-timestamp')

    for t in transactions:
        writer.writerow([
            t.sender.user.username if t.sender else '-',
            t.receiver.user.username if t.receiver else '-',
            t.amount,
            t.transaction_type,
            t.status,
            t.timestamp
        ])

    return response