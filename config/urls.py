#
# Fichier de routage principal du projet Django (config/urls.py)
# Définit les routes globales du projet : admin, authentification, dashboard, home, gestion des utilisateurs, suppression de publication, etc.
# Inclus les routes de l'application core via include('core.urls')
#
from django.contrib import admin
from django.urls import path, include
from core.views import CustomSignupView, dashboard, check_username, delete_publication
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Accès à l'interface d'administration Django
    path('admin/', admin.site.urls),
    # Inscription personnalisée
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    # Authentification (allauth)
    path('accounts/', include('allauth.urls')),
    # Page d'accueil publique
    path('', views.home, name='home'),
    # Tableau de bord étudiant
    path('dashboard/', dashboard, name='dashboard'),
    # Vérification d'unicité du username (AJAX)
    path('check-username/', views.check_username, name='check_username'),
    # Vérification d'unicité du matricule (AJAX)
    path('check-matricule/', views.check_matricule, name='check_matricule'),
    # Suppression d'une publication
    path('publication/delete/<int:pk>/', delete_publication, name='delete_publication'),
    # Inclusion des routes de l'application core
    path('core/', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
