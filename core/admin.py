#
# Fichier d'administration Django pour l'application core
# Permet la gestion des modèles principaux via l'interface d'administration :
# - CustomUser : gestion des utilisateurs personnalisés
# - Publication : gestion des publications scientifiques
# - Commentaire : gestion des commentaires sur les publications
# - Reponse : gestion des réponses aux commentaires
# - Communique : gestion des communiqués administratifs
#

from django.contrib import admin
from .models import CustomUser, Publication, Commentaire, Reponse, Communique

# Enregistrement des modèles dans l'interface d'administration
admin.site.register(CustomUser)
admin.site.register(Publication)
admin.site.register(Commentaire)
admin.site.register(Reponse)
admin.site.register(Communique)
