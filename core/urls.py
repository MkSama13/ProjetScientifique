from django.urls import path
from .views import add_commentaire, delete_commentaire

urlpatterns = [
    # ...existing code...
    path('publication/<int:pub_id>/commentaire/', add_commentaire, name='add_commentaire'),
    path('commentaire/<int:pk>/delete/', delete_commentaire, name='delete_commentaire'),
    # ...existing code...
]