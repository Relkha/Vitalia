from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .forms import ContactForm, ConnexionForm
from .models.MessageContact import MessageContact
from .models.Profil import Profil
from .models.Objets import ObjectPermission, ConnectedObject, PermissionType
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from vitalia_app.models import Visit
from vitalia_app.models.chambre import Chambre
from vitalia_app.models.Objets import ConnectedObject
from datetime import date
from django.contrib.auth import get_user_model


User = get_user_model()

@login_required
def reservation_visite(request):
    user = request.user
    peut_choisir_resident = False
    residents = None
    selected_resident_id = request.GET.get('resident')

    try:
        selected_resident_id = int(selected_resident_id)
    except (TypeError, ValueError):
        selected_resident_id = None

    # Vérifier le groupe
    if user.groups.filter(name__in=["Réceptionniste", "Visiteur des résidents"]).exists():
        peut_choisir_resident = True
        residents = User.objects.filter(groups__name="Retraité")
    elif user.groups.filter(name="Retraité").exists():
        selected_resident_id = user.id
    else:
        return redirect('dashboard')

    # POST pour créer la visite
    if request.method == 'POST':
        date_visite = request.POST.get('date')
        time_visite = request.POST.get('time')
        resident_id_post = request.POST.get('resident') or selected_resident_id

        try:
            resident_id_post = int(resident_id_post)
        except (TypeError, ValueError):
            resident_id_post = None

        if resident_id_post and date_visite and time_visite:
            resident = User.objects.get(id=resident_id_post)
            Visit.objects.create(
                resident=resident,
                date=date_visite,
                time=time_visite,
                status='validated'
            )
            return redirect(f'/reservation-visite/?resident={resident.id}')

    # Visites prévues
    visites = []
    if selected_resident_id:
        visites = Visit.objects.filter(resident_id=selected_resident_id).order_by('date', 'time')

    # Photo du résident
    photo_resident = None
    if selected_resident_id:
        try:
            profil = Profil.objects.get(user_id=selected_resident_id)
            if profil.photo:
                photo_resident = profil.photo.url
        except Profil.DoesNotExist:
            pass

    context = {
        'peut_choisir_resident': peut_choisir_resident,
        'residents': residents,
        'visites': visites,
        'selected_resident_id': selected_resident_id,
        'photo_resident': photo_resident,
    }

    return render(request, 'vitalia_app/reservation_visite.html', context)

@login_required
def surveillance_view(request):
    if not hasattr(request.user, 'profil') or request.user.profil.get_role() not in [
        'Responsable du site', 'Directeur', 'Chef des infirmiers', 'Réceptionniste'
    ]:
        return redirect('/')

    chambres = Chambre.objects.all()
    objets_connectes = ConnectedObject.objects.all()

    return render(request, 'vitalia_app/surveillance.html', {
        'chambres': chambres,
        'objets_connectes': objets_connectes,
    })

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
                return redirect('dashboard')
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

            MessageContact.objects.create(
                nom=nom,
                email=email,
                objet=objet,
                message=message
            )

            full_message = f"Objet : {objet}\n\nMessage : {message}"
            send_mail(
                subject=f"Nouveau message de {nom} - {objet}",
                message=full_message,
                from_email=email,
                recipient_list=['matheo.arondeau@gmail.com', email],
            )

            return render(request, "contact.html", {
                'form': ContactForm(),
                'success': True
            })
    else:
        form = ContactForm()

    return render(request, "contact.html", {'form': form})

def message_admin(request):
    messages = MessageContact.objects.order_by('-date_envoi')
    return render(request, 'vitalia_app/message_admin.html', {'messages': messages})

@csrf_exempt
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

@login_required
def dashboard(request):
    user = request.user

    if not hasattr(user, "profil"):
        Profil.objects.create(user=user)

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

@login_required
def connected_objects(request):
    user_groups = request.user.groups.all()
    object_permissions = ObjectPermission.objects.filter(group__in=user_groups).select_related('connected_object').prefetch_related('permissions')

    objets_affichables = {}

    for op in object_permissions:
        obj = op.connected_object
        if obj.id not in objets_affichables:
            objets_affichables[obj.id] = {
                "objet": obj,
                "permissions": set()
            }
        objets_affichables[obj.id]["permissions"].update(p.code for p in op.permissions.all())

    return render(request, 'connected_objets.html', {"objets": objets_affichables.values()})
