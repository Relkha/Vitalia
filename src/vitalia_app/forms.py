from django import forms
from .models.Evenement import Evenement
from .models.Chambre import Chambre
from django.contrib.auth.models import User
from django import forms
from .models.Profil import Profil

from .models import DossierMedical

from django import forms
from .models import ConnectedObject

class ConnectedObjectForm(forms.ModelForm):
    class Meta:
        model = ConnectedObject
        fields = ['name', 'type', 'description', 'status', 'value', 'room']

class DossierMedicalForm(forms.ModelForm):
    class Meta:
        model = DossierMedical
        fields = ['etat', 'consultation', 'observations']
        widgets = {
            'etat': forms.TextInput(attrs={'placeholder': 'État de santé'}),
            'consultation': forms.Textarea(attrs={'rows': 4}),
            'observations': forms.Textarea(attrs={'rows': 4}),
        }

class ContactForm(forms.Form):
    OBJET_CHOICES = [
        ('compte', 'Demande de création de compte / inscription'),
        ('infos', 'Demande d\'informations'),
        ('visite', 'Demande de visite'),
        ('disponibilite', 'Demande de disponibilités'),
        ('recrutement', 'Candidature / Recrutement'),
        ('partenariat', 'Demande de partenariat'),
        ('autre', 'Autre demande'),
    ]

    nom = forms.CharField(max_length=100, label="Nom complet")
    email = forms.EmailField(label="Adresse e-mail")
    objet = forms.ChoiceField(choices=OBJET_CHOICES, label="Objet de la demande")
    message = forms.CharField(widget=forms.Textarea, label="Votre message")

class ConnexionForm(forms.Form):
    Nom = forms.CharField(max_length=100, label="Nom d'utilisateur")
    mdp = forms.CharField(max_length=100, label="Mot de passe", widget=forms.PasswordInput)




class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['user', 'subject', 'start_time', 'end_time']



class ChambreForm(forms.ModelForm):
    resident = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Retraité"),
        required=False,
        empty_label="Aucun résident",
        label="Résident"
    )

    class Meta:
        model = Chambre
        fields = ['statut', 'resident']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resident'].label_from_instance = self.get_resident_label

    def get_resident_label(self, user):
        if user.first_name or user.last_name:
            full_name = f"{user.first_name} {user.last_name}".strip()
            return f"{full_name} ({user.username})"
        else:
            return user.username

    def clean(self):
        cleaned_data = super().clean()
        statut = cleaned_data.get('statut')
        resident = cleaned_data.get('resident')

        #Si statut est LIBRE, aucun résident ne doit être assigné
        if statut == 'LIBRE' and resident is not None:
            raise forms.ValidationError(
                "Une chambre libre ne peut pas avoir de résident assigné."
            )

        #Si statut est OCCUPE ou RESERVE, un résident doit être assigné
        if statut in ['OCCUPE', 'RESERVE'] and resident is None:
            raise forms.ValidationError(
                "Une chambre occupée ou réservée doit avoir un résident assigné."
            )

        return cleaned_data

class ProfilForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['photo']

from django import forms

class DemandeCompteForm(forms.Form):
    nom = forms.CharField(max_length=100, required=True, label="Nom")
    prenom = forms.CharField(max_length=100, required=True, label="Prénom")
    email = forms.EmailField(required=True, label="Email")
    raison = forms.CharField(widget=forms.Textarea, required=True, label="Raison de la demande")



