#
# Fichier de routage des URLs de l'application core
# Définit les routes pour les vues principales : dashboard, publications, commentaires, réponses, statistiques, notifications, etc.
# Chaque route est associée à une vue correspondante dans views.py
#
from django.urls import path
from .views import (
    add_commentaire, delete_commentaire, add_reponse, delete_reponse, 
    edit_publication, bloc_activite_notifications, bloc_statistiques, 
    dashboard, publications_list, stream_updates
)

urlpatterns = [
    # SSE Streams
    path('stream_updates/', stream_updates, name='stream_updates'),
    # Tableau de bord étudiant
    path('dashboard/', dashboard, name='dashboard'),
    # Liste des publications
    path('publications/', publications_list, name='publications_list'),
    # Ajout d'un commentaire à une publication
    path('publication/<int:pub_id>/commentaire/', add_commentaire, name='add_commentaire'),
    # Suppression d'un commentaire
    path('commentaire/<int:pk>/delete/', delete_commentaire, name='delete_commentaire'),
]

urlpatterns += [
    # Ajout d'une réponse à un commentaire
    path('commentaire/<int:commentaire_id>/reponse/', add_reponse, name='add_reponse'),
    # Suppression d'une réponse
    path('reponse/<int:pk>/delete/', delete_reponse, name='delete_reponse'),
    # Edition d'une publication
    path('publication/<int:pk>/edit/', edit_publication, name='edit_publication'),
]

urlpatterns += [
    # Bloc notifications d'activité (HTMX)
    path('dashboard/activite-notifications/', bloc_activite_notifications, name='bloc_activite_notifications'),
    # Bloc statistiques (HTMX)
    path('dashboard/statistiques/', bloc_statistiques, name='bloc_statistiques'),
]
