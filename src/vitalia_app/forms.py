from django import forms

class ContactForm(forms.Form):
    OBJET_CHOICES = [
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


