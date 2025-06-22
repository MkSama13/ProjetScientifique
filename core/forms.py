from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from .models import Publication, Commentaire, Reponse

User = get_user_model()

# Formulaire d'inscription personnalisé avec champs supplémentaires
class CustomSignupForm(SignupForm):
    promotion = forms.CharField(max_length=100, label='Promotion')
    matricule = forms.CharField(
        max_length=20,
        required=False,
        help_text="Les matricules commencent par INFO, EQ, ETT..."
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip().upper()
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur appartient déjà à un compte existant!")
        if username != self.cleaned_data['username']:
            raise ValidationError("Le nom d'utilisateur doit être en MAJUSCULES.")
        return username

    def clean_matricule(self):
        matricule = self.cleaned_data.get('matricule', '').strip().upper()
        if matricule:
            if User.objects.filter(matricule=matricule).exists():
                raise ValidationError("Ce matricule appartient déjà à un compte")
        return matricule

    # Sauvegarde des données supplémentaires dans l'utilisateur
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.promotion = self.cleaned_data['promotion']
        user.matricule = self.cleaned_data.get('matricule', '')
        user.save()
        return user

# Formulaire de connexion personnalisé avec confirmation du mot de passe
class CustomLoginForm(LoginForm):
    full_name = forms.CharField(max_length=150, label='Nom d\'utilisateur')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmation du mot de passe')

    # Validation pour vérifier que les mots de passe correspondent
    def clean(self):
        cleaned_data = super().clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        # Vérification du login (nom d'utilisateur)
        if login and not User.objects.filter(username=login.upper()).exists():
            raise ValidationError({
                'login': "Ce nom d'utilisateur ne correspont à aucun compte existant"
            })
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Les mots de passe ne sont pas identiques.")
        return cleaned_data

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['titre', 'contenu', 'departement', 'promotion', 'fichier', 'tags']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-transparent border border-blue-400/30 text-white placeholder:text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition', 'placeholder': 'Titre...'}),
            'contenu': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-transparent border border-blue-400/30 text-white placeholder:text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition', 'rows': 4, 'maxlength': 2000, 'placeholder': 'Exprimez-vous...'}),
            'departement': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-transparent border border-blue-400/30 text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition placeholder:text-blue-200 appearance-none'}),
            'promotion': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-transparent border border-blue-400/30 text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition placeholder:text-blue-200 appearance-none'}),
            'fichier': forms.ClearableFileInput(attrs={'class': 'block w-full text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 transition file:transition-transform file:duration-200', 'accept': 'image/*,application/pdf'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-transparent border border-blue-400/30 text-white placeholder:text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition', 'placeholder': 'Tags (séparés par des virgules)'}),
        }

class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-[#181f36] border border-blue-400/30 text-white placeholder:text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition',
                'rows': 2,
                'maxlength': 500,
                'placeholder': 'Écrire un commentaire...'
            })
        }

class ReponseForm(forms.ModelForm):
    class Meta:
        model = Reponse
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'w-full px-3 py-1 rounded-lg bg-[#181f36] border border-blue-400/30 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 1,
                'maxlength': 300,
                'placeholder': 'Répondre...'
            })
        }
