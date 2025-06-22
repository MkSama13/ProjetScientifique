from django.urls import path
from .views import add_commentaire, delete_commentaire, add_reponse, delete_reponse, edit_publication, bloc_activite_notifications, bloc_statistiques

urlpatterns = [
    # ...existing code...
    path('publication/<int:pub_id>/commentaire/', add_commentaire, name='add_commentaire'),
    path('commentaire/<int:pk>/delete/', delete_commentaire, name='delete_commentaire'),
]

urlpatterns += [
    path('commentaire/<int:commentaire_id>/reponse/', add_reponse, name='add_reponse'),
    path('reponse/<int:pk>/delete/', delete_reponse, name='delete_reponse'),
    path('publication/<int:pk>/edit/', edit_publication, name='edit_publication'),
]

urlpatterns += [
    path('dashboard/activite-notifications/', bloc_activite_notifications, name='bloc_activite_notifications'),
    path('dashboard/statistiques/', bloc_statistiques, name='bloc_statistiques'),
]