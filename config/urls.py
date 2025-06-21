from django.contrib import admin
from django.urls import path, include
from core.views import CustomSignupView, dashboard, check_username, delete_publication
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/', include('allauth.urls')),
    path('', views.home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('check-username/', views.check_username, name='check_username'),
    path('check-matricule/', views.check_matricule, name='check_matricule'),
    path('publication/delete/<int:pk>/', delete_publication, name='delete_publication'),
]
