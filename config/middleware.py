from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings

class CustomCsrfExemptMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(request, 'csrf_processing_done', False):
            return None

        # Liste des chemins d'URL à exclure de la vérification CSRF
        # Utilisez des expressions régulières si nécessaire
        # ATTENTION : N'excluez des routes que si vous êtes absolument certain
        # qu'elles sont protégées par d'autres moyens.
        CSRF_EXEMPT_URLS = [
            '/core/publications/', # Exclu temporairement pour débogage
            # '/api/webhook/', # Exemple d'URL à exclure
            # Ajoutez d'autres chemins ici
        ]

        if request.path in CSRF_EXEMPT_URLS:
            return None # Ne pas appliquer la vérification CSRF pour cette URL

        return super().process_view(request, callback, callback_args, callback_kwargs)
