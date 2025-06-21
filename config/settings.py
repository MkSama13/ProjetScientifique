"""
Paramètres Django pour le projet config.

Généré par 'django-admin startproject' avec Django 5.2.2.

Pour plus d'informations sur ce fichier, voir
https://docs.djangoproject.com/en/5.2/topics/settings/

Pour la liste complète des paramètres et leurs valeurs, voir
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os
from django.core.validators import RegexValidator

# Construction des chemins dans le projet, par exemple BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Paramètres de démarrage rapide - non adaptés pour la production
# Voir https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# AVERTISSEMENT DE SÉCURITÉ : garder la clé secrète utilisée en production secrète !
SECRET_KEY = 'django-insecure-e7paa-36ap72na8p=qo095h5e#=7geh^w)+y3$8rde*m*=s-x5'

# AVERTISSEMENT DE SÉCURITÉ : ne pas exécuter avec DEBUG activé en production !
DEBUG = True

ALLOWED_HOSTS = []


# Définition des applications installées

INSTALLED_APPS = [
    'django.contrib.admin',  # Interface d'administration Django
    'django.contrib.auth',  # Système d'authentification
    'django.contrib.contenttypes',  # Gestion des types de contenu
    'django.contrib.sessions',  # Gestion des sessions
    'django.contrib.messages',  # Gestion des messages
    'django.contrib.staticfiles',  # Gestion des fichiers statiques
    'core',  # Application principale du projet
    'widget_tweaks',  # Application tierce pour personnaliser les widgets
    'taggit',  # Application tierce pour la gestion des tags
    'django.contrib.sites',  # Framework des sites Django
    'allauth',  # Application tierce pour l'authentification
    'allauth.account',  # Gestion des comptes avec allauth
    'allauth.socialaccount',  # Gestion des comptes sociaux avec allauth
    'imagekit',  # Application tierce pour le traitement d'images
]

# Middleware utilisés par le projet
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Sécurité
    'django.contrib.sessions.middleware.SessionMiddleware',  # Sessions
    'django.middleware.common.CommonMiddleware',  # Middleware commun
    'django.middleware.csrf.CsrfViewMiddleware',  # Protection CSRF
    'allauth.account.middleware.AccountMiddleware',  # Middleware allauth
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Authentification
    'django.contrib.messages.middleware.MessageMiddleware',  # Messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protection clickjacking
]

# Configuration des URLs racines
ROOT_URLCONF = 'config.urls'

# Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR / 'templates')],  # Répertoire des templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  # Contexte des requêtes
                'django.contrib.auth.context_processors.auth',  # Contexte d'authentification
                'django.contrib.messages.context_processors.messages',  # Contexte des messages
            ],
        },
    },
]

# Application WSGI
WSGI_APPLICATION = 'config.wsgi.application'


# Base de données
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Moteur SQLite
        'NAME': BASE_DIR / 'db.sqlite3',  # Nom du fichier de base de données
    }
}

# Django-Allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Backend d'authentification Django
    'allauth.account.auth_backends.AuthenticationBackend',  # Backend allauth
]

SITE_ID = 1

# Champs du formulaire d'inscription
# Paramètres mis à jour pour éviter les avertissements de dépréciation
ACCOUNT_LOGIN_METHODS = {'username'}
ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*', 'departement', 'promotion']

# Formulaires personnalisés
ACCOUNT_FORMS = {
    'signup': 'core.forms.CustomSignupForm',
}

# URLs de redirection après inscription, connexion, déconnexion
ACCOUNT_SIGNUP_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'core.CustomUser'


# Validation des mots de passe
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalisation
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'fr'  # Langue par défaut

TIME_ZONE = 'Africa/Kinshasa'  # Fuseau horaire

USE_I18N = True  # Activation de la traduction

USE_TZ = True  # Activation de la gestion des fuseaux horaires


# Fichiers statiques (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Type de champ clé primaire par défaut
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ajout d'un validateur personnalisé pour accepter les espaces dans le nom d'utilisateur

USERNAME_REGEX = r'^[\w.@+\- ]+$'  # Lettres, chiffres, @ . + - _ et espace
USERNAME_MESSAGE = "Saisissez un nom d’utilisateur valide. Il ne peut contenir que des lettres, des nombres, des espaces ou les caractères « @ », « . », « + », « - » et « _ »."

# Si vous avez un modèle utilisateur personnalisé, ajoutez ce validateur dans le champ username du modèle core.CustomUser :
# username = models.CharField(
#     max_length=150,
#     unique=True,
#     validators=[RegexValidator(USERNAME_REGEX, USERNAME_MESSAGE)],
#     ...
# )
