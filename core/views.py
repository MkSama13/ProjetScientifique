from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView
from .forms import CustomSignupForm, PublicationForm
from .models import Publication
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.contrib.auth import get_user_model

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    # Utilisation de la méthode recommandée pour détecter une requête HTMX
    is_htmx = request.headers.get('HX-Request') == 'true'
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.auteur = request.user
            publication.save()
            if is_htmx:
                # Affichage dynamique : insérer la nouvelle publication en haut de la liste
                return render(request, 'core/partials/publication_card.html', {'pub': publication, 'user': request.user})
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = PublicationForm()
    publications = Publication.objects.all()
    if is_htmx:
        return render(request, 'core/partials/publications_list.html', {'publications': publications, 'user': request.user})
    return render(request, 'core/dashboard_etudiant.html', {"user": request.user, 'form': form, 'publications': publications})

class CustomSignupView(SignupView):
    template_name = 'account/signup.html'
    form_class = CustomSignupForm

    def get_success_url(self):
        from django.urls import reverse
        return reverse('dashboard')

def check_username(request):
    username = request.GET.get('username', '').strip().upper()
    User = get_user_model()
    exists = User.objects.filter(username=username).exists()
    if exists:
        return HttpResponse('<p class="text-red-500 text-xs italic">Ce nom d\'utilisateur appartient déjà à un compte veuillez en saisir un autre</p>')
    return HttpResponse('')

def check_matricule(request):
    matricule = request.GET.get('matricule', '').strip().upper()
    User = get_user_model()
    exists = User.objects.filter(matricule=matricule).exists()
    if exists:
        return HttpResponse('<p class="text-red-500 text-xs italic">Ce matricule appartient déjà à un compte</p>')
    return HttpResponse('')

@require_POST
def delete_publication(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    try:
        pub = Publication.objects.get(pk=pk)
    except Publication.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Publication introuvable'}, status=404)
    if pub.auteur_id != request.user.id:
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    pub.delete()
    # Retourner une réponse vide pour HTMX (pas de JSON, pas de texte)
    return HttpResponse(status=204)
