from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.urls import reverse
from django.template.loader import render_to_string
import json
import time
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView
from .forms import CustomSignupForm, PublicationForm, CommentaireForm, ReponseForm, CommuniqueForm
from .models import Publication, Commentaire, Reponse, Communique, PublicationImage
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Prefetch
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils import timezone

# ==========================
# Vues principales de l'application
# ==========================

def home(request):
    """
    Vue d'accueil de la plateforme.
    """
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    """
    Tableau de bord étudiant : création et affichage des publications de l'utilisateur connecté.
    Gère aussi l'ajout d'images multiples à une publication.
    """
    is_htmx = request.headers.get('HX-Request') == 'true'
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.auteur = request.user
            publication.save()
            # Gestion des images multiples
            images = request.FILES.getlist('images')
            for img in images:
                PublicationImage.objects.create(publication=publication, image=img)
            # Gestion des vidéos multiples
            videos = request.FILES.getlist('videos')
            for v in videos[:4]:
                from .models import PublicationVideo
                PublicationVideo.objects.create(publication=publication, video=v)
            # Gestion des fichiers PDF multiples
            pdfs = request.FILES.getlist('pdfs')
            for pdf_file in pdfs:
                from .models import PublicationPDF
                PublicationPDF.objects.create(publication=publication, pdf=pdf_file)

            # Notify SSE stream
            html_content = render_to_string('core/partials/publication_card.html', {'pub': publication, 'user': request.user})
            notify_event('new_publication', {'id': publication.id, 'html': html_content})

            if is_htmx:
                return render(request, 'core/partials/publication_card.html', {'pub': publication, 'user': request.user})
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = PublicationForm()
    # Publications de l'utilisateur avec préchargement optimisé
    tag_query = request.GET.get('tags', '').strip()
    
    # Base queryset
    publications_qs = Publication.objects.filter(auteur=request.user)
    
    # Filtrage par tags si nécessaire
    if tag_query:
        tag_list = [t.strip().lower() for t in tag_query.split(',') if t.strip()]
        if tag_list:
            q = Q()
            for tag in tag_list:
                q |= Q(tags__icontains=tag)
            publications_qs = publications_qs.filter(q)

    # Préchargement optimisé des commentaires et des réponses
    publications = publications_qs.prefetch_related(
        Prefetch('commentaires', queryset=Commentaire.objects.filter(is_deleted=False).order_by('date_commentaire').prefetch_related(
            Prefetch('reponses', queryset=Reponse.objects.filter(is_deleted=False).order_by('date_reponse'))
        ))
    )

    commentaire_form = CommentaireForm()
    for pub in publications:
        pub.commentaire_form = commentaire_form
        pub.commentaire_action_url = reverse('add_commentaire', args=[pub.pk])
        # Le template utilise `prefetched_commentaires`, donc nous assignons les commentaires déjà chargés
        pub.prefetched_commentaires = pub.commentaires.all()
        # La propriété `has_mixed_file_types` est aussi utilisée
        if callable(pub.has_mixed_file_types):
            pub.has_mixed_file_types = pub.has_mixed_file_types()
    # Statistiques utilisateur
    nb_publications = publications.count()
    nb_commentaires = Commentaire.objects.filter(auteur=request.user).count()
    # Activité et notifications récentes
    activites = Commentaire.objects.filter(auteur=request.user).order_by('-date_commentaire')[:10]
    notifications = Commentaire.objects.filter(publication__auteur=request.user).exclude(auteur=request.user).order_by('-date_commentaire')[:10]
    if is_htmx:
        return render(request, 'core/partials/publications_list.html', {'publications': publications, 'user': request.user})
    return render(request, 'core/dashboard_etudiant.html', {
        "user": request.user,
        'form': form,
        'publications': publications,
        'nb_publications': nb_publications,
        'nb_commentaires': nb_commentaires,
        'activites': activites,
        'notifications': notifications,
    })

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
    
    pub.is_deleted = True
    pub.save()

    # Notify the deletion stream
    notify_event('delete_publication', {'id': pub.id})

    return HttpResponse(status=204)

@login_required
@require_POST
def add_commentaire(request, pub_id):
    pub = Publication.objects.get(pk=pub_id)
    form = CommentaireForm(request.POST, request.FILES)
    if form.is_valid():
        commentaire = form.save(commit=False)
        commentaire.auteur = request.user
        commentaire.publication = pub
        # Gestion des fichiers uploadés
        if form.cleaned_data.get('image'):
            commentaire.image = form.cleaned_data['image']
        if form.cleaned_data.get('video'):
            commentaire.video = form.cleaned_data['video']
        if form.cleaned_data.get('pdf'):
            commentaire.pdf = form.cleaned_data['pdf']
        commentaire.save()

        # Notify SSE stream
        html_content = render_to_string('core/partials/commentaire_item.html', {'commentaire': commentaire, 'user': request.user})
        notify_event('new_comment', {
            'id': commentaire.id, 
            'publication_id': commentaire.publication_id, 
            'html': html_content
        })

        # Rendu du commentaire seul pour insertion dynamique
        return render(request, 'core/partials/commentaire_item.html', {'commentaire': commentaire, 'user': request.user})
    # Rendu du formulaire avec erreurs
    return render(request, 'core/partials/commentaire_form.html', {'form': form, 'pub': pub, 'action_url': reverse('add_commentaire', args=[pub_id])})

@login_required
@require_POST
def delete_commentaire(request, pk):
    try:
        commentaire = Commentaire.objects.get(pk=pk)
    except Commentaire.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Commentaire introuvable'}, status=404)
    if commentaire.auteur != request.user:
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    commentaire.is_deleted = True
    commentaire.save()

    # Notify the deletion stream
    notify_event('delete_comment', {'id': commentaire.id, 'publication_id': commentaire.publication_id})

    return HttpResponse(status=204)

@login_required
@require_POST
def add_reponse(request, commentaire_id):
    from django.shortcuts import get_object_or_404
    commentaire = get_object_or_404(Commentaire, pk=commentaire_id)
    form = ReponseForm(request.POST, request.FILES)
    if form.is_valid():
        reponse = form.save(commit=False)
        reponse.auteur = request.user
        reponse.commentaire = commentaire
        
        parent_id = request.POST.get('parent')
        is_nested_reply = False
        if parent_id:
            from core.models import Reponse
            try:
                reponse.parent = Reponse.objects.get(pk=parent_id)
                is_nested_reply = True
            except Reponse.DoesNotExist:
                reponse.parent = None

        if form.cleaned_data.get('image'): reponse.image = form.cleaned_data['image']
        if form.cleaned_data.get('video'): reponse.video = form.cleaned_data['video']
        if form.cleaned_data.get('pdf'): reponse.pdf = form.cleaned_data['pdf']
        reponse.save()

        # Notify SSE stream
        html_content = render_to_string('core/partials/reponse_item.html', {'reponse': reponse, 'user': request.user})
        notify_event('new_reply', {
            'id': reponse.id, 
            'comment_id': reponse.commentaire_id, 
            'parent_id': reponse.parent_id, 
            'html': html_content
        })

        # Si c'est une réponse imbriquée, ne renvoyer que l'item.
        # Sinon, renvoyer le wrapper complet.
        if is_nested_reply:
            return render(request, 'core/partials/reponse_item.html', {'reponse': reponse, 'user': request.user})
        else:
            return render(request, 'core/partials/reponses_wrapper.html', {'commentaire': commentaire, 'user': request.user})
            
    return HttpResponse(status=400)

@login_required
@require_POST
def edit_publication(request, pk):
    pub = Publication.objects.get(pk=pk)
    if pub.auteur != request.user:
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    titre = request.POST.get('titre', '').strip()
    contenu = request.POST.get('contenu', '').strip()
    if not titre or not contenu:
        return JsonResponse({'success': False, 'error': 'Champs requis'}, status=400)
    pub.titre = titre
    pub.contenu = contenu
    pub.save()
    # Renvoie la carte publication mise à jour (pour HTMX)
    return render(request, 'core/partials/publication_card.html', {'pub': pub, 'user': request.user})

@login_required
@require_GET
def bloc_activite_notifications(request):
    notifications = []
    # Commentaires sur les publications de l'utilisateur
    notif_comment = Commentaire.objects.filter(publication__auteur=request.user).exclude(auteur=request.user).order_by('-date_commentaire')[:5]
    for notif in notif_comment:
        notifications.append({
            'type': 'commentaire',
            'auteur': notif.auteur,
            'date': notif.date_commentaire,
            'message': f"{notif.auteur.get_full_name() or notif.auteur.username} a commenté une de vos publications"
        })
    # Réponses à un commentaire de l'utilisateur
    notif_reponse = Reponse.objects.filter(commentaire__auteur=request.user).exclude(auteur=request.user).order_by('-date_reponse')[:5]
    for notif in notif_reponse:
        notifications.append({
            'type': 'reponse',
            'auteur': notif.auteur,
            'date': notif.date_reponse,
            'message': f"{notif.auteur.get_full_name() or notif.auteur.username} a répondu à votre commentaire"
        })
    # Communiqués de l'administration (notification automatique)
    from .models import Communique
    dernier_communique = Communique.objects.order_by('-date_pub').first()
    if dernier_communique:
        notifications.append({
            'type': 'admin',
            'auteur': None,
            'date': dernier_communique.date_pub,
            'message': f"Nouveau communiqué : {dernier_communique.titre}"
        })
    # On trie toutes les notifications par date décroissante et on garde les 5 plus récentes
    notifications = sorted(notifications, key=lambda n: n['date'], reverse=True)[:5]
    return render(request, 'core/partials/activite_notifications.html', {
        'notifications': notifications,
    })

@login_required
@require_GET
def bloc_statistiques(request):
    user_publications = Publication.objects.filter(auteur=request.user)
    nb_publications = user_publications.count()
    # Compte tous les commentaires et toutes les réponses de l'utilisateur
    nb_commentaires = Commentaire.objects.filter(auteur=request.user).count() + Reponse.objects.filter(auteur=request.user).count()
    nb_fichiers = 0  # Désactivé : plus d'upload de fichiers (image/pdf unique)
    return render(request, 'core/partials/statistiques.html', {
        'nb_publications': nb_publications,
        'nb_commentaires': nb_commentaires,
        'nb_fichiers': nb_fichiers,
    })

def publications_list(request):
    from django.db.models import Prefetch
    # Recherche par tags (GET)
    tag_query = request.GET.get('tags', '').strip()
    
    # Base queryset
    publications_qs = Publication.objects.filter(is_deleted=False).order_by('-date_pub')

    # Filtrage par tags si nécessaire
    if tag_query:
        tag_list = [t.strip().lower() for t in tag_query.split(',') if t.strip()]
        if tag_list:
            q = Q()
            for tag in tag_list:
                q |= Q(tags__icontains=tag)
            publications_qs = publications_qs.filter(q)

    # Préchargement optimisé des commentaires et des réponses
    publications = publications_qs.prefetch_related(
        Prefetch('commentaires', queryset=Commentaire.objects.filter(is_deleted=False).order_by('date_commentaire').prefetch_related(
            Prefetch('reponses', queryset=Reponse.objects.filter(is_deleted=False).order_by('date_reponse'))
        ))
    )

    commentaire_form = CommentaireForm()
    for pub in publications:
        pub.commentaire_form = commentaire_form
        pub.commentaire_action_url = reverse('add_commentaire', args=[pub.pk])
        # Le template utilise `prefetched_commentaires`, donc nous assignons les commentaires déjà chargés
        pub.prefetched_commentaires = pub.commentaires.all()

    # Si la requête est une requête HTMX, ne retourner que le partial (évite la duplication)
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'core/partials/publications_list.html', {'publications': publications, 'user': request.user})
    return render(request, 'core/publications.html', {
        'publications': publications,
        'user': request.user,
    })

@login_required
@require_POST
def delete_reponse(request, pk):
    try:
        reponse = Reponse.objects.get(pk=pk)
    except Reponse.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Réponse introuvable'}, status=404)
    if reponse.auteur != request.user:
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)

    reponse.is_deleted = True
    reponse.save()

    # Notify the deletion stream
    notify_event('delete_reply', {'id': reponse.id})

    return HttpResponse(status=204)

# ==========================
# SSE : Unified real-time updates for all users (no user filtering)
# ==========================
update_events = []

@ensure_csrf_cookie
def stream_updates(request):
    """
    SSE stream for all real-time updates (comments, replies, deletions, etc.).
    Sends ALL events to ALL clients, no user filtering.
    """
    def event_stream():
        last_processed_event_time = timezone.now()
        while True:
            events_to_send = [e for e in update_events if e['timestamp'] > last_processed_event_time]
            for event in events_to_send:
                yield f"event: {event['name']}\n"
                yield f"data: {json.dumps(event['data'])}\n\n"
            if events_to_send:
                last_processed_event_time = max(e['timestamp'] for e in events_to_send)
            time.sleep(1.5)
            # Clean up old events
            cutoff = timezone.now() - timezone.timedelta(seconds=30)
            update_events[:] = [e for e in update_events if e['timestamp'] > cutoff]
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

def notify_event(event_name, data):
    """
    Adds an event to the file-level cache for SSE streaming.
    """
    update_events.append({
        'timestamp': timezone.now(),
        'name': event_name,
        'data': data
    })
