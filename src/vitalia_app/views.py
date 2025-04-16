from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm, ConnexionForm
from .models.MessageContact import MessageContact
from .models.Profil import Profil

def index(request):
    return render(request, "index.html")

def propos(request):
    return render(request, "a_propos.html")

def deconnexion(request):
    logout(request)
    return render(request, 'deconnexion.html')
def connexion(request):
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['Nom']
            mdp = form.cleaned_data['mdp']

            user = authenticate(request, username=nom, password=mdp)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Change "home" par le nom de ta vue d’accueil
            else:
                error = "Identifiants incorrects. Veuillez réessayer."
                return render(request, 'connexion.html', {'form': form, 'error': error})
    else:
        form = ConnexionForm()

    return render(request, 'connexion.html', {'form': form})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            objet = form.cleaned_data['objet']
            message = form.cleaned_data['message']

            # Enregistrement dans la bdd
            MessageContact.objects.create(
                nom=nom,
                email=email,
                objet=objet,
                message=message
            )

            # Envoi du mail
            full_message = f"Objet : {objet}\n\nMessage : {message}"
            send_mail(
                subject=f"Nouveau message de {nom} - {objet}",
                message=full_message,
                from_email=email,
                recipient_list=['matheo.arondeau@gmail.com', email],  # Ajouter ton adresse dans les destinataires
            )


            return render(request, "contact.html", {
                'form': ContactForm(),
                'success': True
            })
    else:
        form = ContactForm()

    return render(request, "contact.html", {'form': form})

#@login_required
def message_admin(request):
    messages = MessageContact.objects.order_by('-date_envoi') # "-" pour afficher les messgaes du plus récent au plus ancien
    return render(request, 'vitalia_app/message_admin.html', {'messages': messages})

@csrf_exempt  # uniquement pour test
# @login_required
def repondre_message(request, message_id):
    if request.method == 'POST':
        reponse = request.POST.get('reponse')
        message = MessageContact.objects.get(id=message_id)
        
        send_mail(
            subject=f"Réponse à votre message : {message.objet}",
            message=reponse,
            from_email='matheo.arondeau@gmail.com',
            recipient_list=[message.email],
        )
        return redirect('/messages/')

def dashboard(request):
    user = request.user

    # Crée un profil s'il n'existe pas encore (logique métier)
    if not hasattr(user, "profil"):
        Profil.objects.create(user=user)

    # Récupère le groupe (rôle) principal de l'utilisateur
    role = user.groups.first().name if user.groups.exists() else "Aucun"

    context = {
        "role": role,
        "is_admin": role == "Responsable du site",
        "is_directeur": role == "Directeur",
        "is_chef_infirmier": role == "Chef des infirmiers",
        "is_infirmier": role == "Infirmier",
        "is_aide_soignant": role == "Aide-soignant",
        "is_menage": role == "Ménage",
        "is_reception": role == "Réceptionniste",
        "is_visiteur_resident": role == "Visiteur des résidents",
        "is_retraite": role == "Retraité",
        "is_medical": role in ["Infirmier", "Chef des infirmiers", "Aide-soignant"],
        "can_manage_visites": role in ["Réceptionniste", "Visiteur des résidents", "Retraité"],
    }

    if role == "Visiteur du site":
        return render(request, "index.html", context)
    else:
        return render(request, "dashboard.html", context)


