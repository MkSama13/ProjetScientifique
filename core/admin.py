from django.contrib import admin
from .models import CustomUser, Publication, Commentaire, Reponse, Communique

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Publication)
admin.site.register(Commentaire)
admin.site.register(Reponse)
admin.site.register(Communique)
