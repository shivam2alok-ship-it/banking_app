from django.urls import path
from . import views
from .views import profile_view
from .views import support_view

from django.contrib.auth.views import LogoutView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('set-pin/', views.set_pin, name='set_pin'),  # 👈 ADD THIS

    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('transactions/', views.transaction_history, name='transactions'),
    path('statement/', views.download_statement, name='statement'),
    path('profile/', profile_view, name='profile'),
    path('support/', support_view, name='support'),
    path('apply-fd/', views.apply_fd, name='apply_fd'),
    path('support/create/', views.create_request, name='create_request'),
    path('support/my-requests/', views.my_requests, name='my_requests'),
    path('transfer/', views.transfer_view, name='transfer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)