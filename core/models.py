from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

# Modèle utilisateur personnalisé étendant AbstractUser
class CustomUser(AbstractUser):
    # Promotion de l'étudiant
    promotion = models.CharField(max_length=100)
    matricule = models.CharField(max_length=20, blank=True, help_text="Les matricules commencent par INFO, EQ, ETT...")
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+\- ]+$',
            message="Saisissez un nom d’utilisateur valide. Il ne peut contenir que des lettres, des nombres, des espaces ou les caractères « @ », « . », « + », « - » et « _ »."
        )],
        help_text="Requis. 150 caractères ou moins. Lettres, chiffres, espaces et @/./+/-/_ seulement."
    )

# Modèle pour les publications
