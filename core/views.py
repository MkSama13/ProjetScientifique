from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView
from .forms import CustomSignupForm
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard_etudiant.html', {"user": request.user})

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
