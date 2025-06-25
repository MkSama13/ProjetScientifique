#
# Configuration de l'application Django 'core'
# Définit le nom de l'application et le type de champ clé primaire par défaut.
#
from django.apps import AppConfig

class CoreConfig(AppConfig):
    # Type de champ clé primaire par défaut (BigAutoField recommandé pour les nouveaux projets)
    default_auto_field = 'django.db.models.BigAutoField'
    # Nom de l'application (doit correspondre au dossier)
    name = 'core'
