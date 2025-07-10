from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings

# ==========================
# Modèle utilisateur personnalisé
# ==========================
class CustomUser(AbstractUser):
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

# ==========================
# Modèle Publication (post étudiant)
# ==========================
class Publication(models.Model):
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publications')
    titre = models.CharField(max_length=120)
    contenu = models.TextField(max_length=2000)
    departement = models.CharField(max_length=50, blank=True)
    promotion = models.CharField(max_length=50, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Tags séparés par des virgules")
    date_pub = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_pub']

    def __str__(self):
        return f"{self.titre} par {self.auteur}"

    @property
    def has_mixed_file_types(self):
        """
        Returns True if the publication contains mixed file types among images, videos, and pdfs.
        """
        has_images = self.images.exists()
        has_videos = self.videos.exists()
        has_pdfs = self.pdfs.exists()
        types_count = sum([has_images, has_videos, has_pdfs])
        return types_count > 1

# ==========================
# Modèle pour les images associées à une publication
# ==========================
class PublicationImage(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='publications/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image pour {self.publication.titre}"

# ==========================
# Modèle pour les commentaires
# ==========================
class Commentaire(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenu = models.TextField(max_length=500)
    date_commentaire = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='commentaires/images/', blank=True, null=True)
    video = models.FileField(upload_to='commentaires/videos/', blank=True, null=True)
    pdf = models.FileField(upload_to='commentaires/pdfs/', blank=True, null=True)

    class Meta:
        ordering = ['date_commentaire']

    def __str__(self):
        return f"Commentaire de {self.auteur} sur {self.publication}"

# ==========================
# Modèle pour les réponses aux commentaires
# ==========================
class Reponse(models.Model):
    commentaire = models.ForeignKey(Commentaire, on_delete=models.CASCADE, related_name='reponses')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenu = models.TextField(max_length=300)
    date_reponse = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='reponses')
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='reponses/images/', blank=True, null=True)
    video = models.FileField(upload_to='reponses/videos/', blank=True, null=True)
    pdf = models.FileField(upload_to='reponses/pdfs/', blank=True, null=True)

    class Meta:
        ordering = ['date_reponse']

    def __str__(self):
        return f"Réponse de {self.auteur} au commentaire {self.commentaire_id}"

# ==========================
# Modèle pour les communiqués (annonces admin)
# ==========================
class Communique(models.Model):
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='communiques')
    titre = models.CharField(max_length=120)
    contenu = models.TextField(max_length=2000)
    date_pub = models.DateTimeField(auto_now_add=True)
    fichier = models.FileField(upload_to='communiques/', blank=True, null=True)

    class Meta:
        ordering = ['-date_pub']

    def __str__(self):
        return f"Communiqué: {self.titre} par {self.auteur}"

# ==========================
# Modèle pour les vidéos associées à une publication
# ==========================
class PublicationVideo(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='publications/videos/', help_text='Formats acceptés : mp4, avi, mov')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vidéo pour {self.publication.titre}"

# ==========================
# Modèle pour les fichiers PDF associés à une publication
# ==========================
class PublicationPDF(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='pdfs')
    pdf = models.FileField(upload_to='publications/pdfs/', help_text='Format accepté : pdf')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF pour {self.publication.titre}"
