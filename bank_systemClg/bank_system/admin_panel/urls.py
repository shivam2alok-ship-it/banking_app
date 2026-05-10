from django.urls import path
from . import views

urlpatterns = [

    # =========================================
    # AUTH
    # =========================================

    path(
        'admin-login/',
        views.admin_login,
        name='admin_login'
    ),

    path(
        'logout/',
        views.admin_logout,
        name='admin_logout'
    ),


    # =========================================
    # DASHBOARD
    # =========================================

    path(
        '',
        views.admin_dashboard,
        name='admin_dashboard'
    ),


    # =========================================
    # USERS
    # =========================================

    path(
        'users/',
        views.manage_users,
        name='manage_users'
    ),

    path(
        'users/<int:user_id>/',
        views.user_detail,
        name='user_detail'
    ),

    path(
        'freeze/<int:user_id>/',
        views.freeze_account,
        name='freeze_account'
    ),

    path(
        'activate/<int:user_id>/',
        views.activate_account,
        name='activate_account'
    ),


    # =========================================
    # TRANSACTIONS
    # =========================================

    path(
        'reports/',
        views.reports_view,
        name='all_transactions'
    ),


    # =========================================
    # SUPPORT
    # =========================================

    path(
        'support/',
        views.support_requests,
        name='support_requests'
    ),


    # =========================================
    # FIXED DEPOSITS
    # =========================================

    path(
        'fixed-deposits/',
        views.fixed_deposits,
        name='fixed_deposits'
    ),


    # =========================================
    # SECURITY PANEL
    # =========================================

    path(
        'security/',
        views.security_panel,
        name='security_panel'
    ),
    
    # =========================================
# QUICK ACTIONS
# =========================================

path(
    'add-user/',
    views.add_user,
    name='add_user'
),

path(
    'freeze-accounts/',
    views.freeze_accounts,
    name='freeze_accounts'
),

path(
    'verify-kyc/',
    views.verify_kyc,
    name='verify_kyc'
),

path(
    'approve-kyc/<int:user_id>/',
    views.approve_kyc,
    name='approve_kyc'
),

path(
    'reject-kyc/<int:user_id>/',
    views.reject_kyc,
    name='reject_kyc'
),

path('admin-panel/reports/', views.reports_view, name='reports'),

path(
    'admin-panel/reports/export/csv/',
    views.export_transactions_csv,
    name='export_transactions_csv'
),

]