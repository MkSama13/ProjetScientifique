from django.apps import AppConfig

# Configuration de l'application 'core'
class CoreConfig(AppConfig):
    # Type de champ clé primaire par défaut
    default_auto_field = 'django.db.models.BigAutoField'
    # Nom de l'application
    name = 'core'
