import json
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .forms import ContactForm, ConnexionForm
from .models.MessageContact import MessageContact
from .models.Profil import Profil
from .models.Objets import ObjectPermission, ConnectedObject, PermissionType
from .models.planning_resident import PlanningEventResident
from .models.Chambre import Chambre
from .models.Evenement import Evenement  
from .models.planning_infirmier import PlanningEventInfirmier
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer
from .forms import EvenementForm



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
            MessageContact.objects.create(nom=nom, email=email, objet=objet, message=message)
            full_message = f"Objet : {objet}\n\nMessage : {message}"
            send_mail(
                subject=f"Nouveau message de {nom} - {objet}",
                message=full_message,
                from_email=email,
                recipient_list=['matheo.arondeau@gmail.com', email],
            )
            return render(request, "contact.html", {'form': ContactForm(), 'success': True})
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



@csrf_exempt
def planning_events_api(request):
    if request.method == "GET":
        events = PlanningEvent.objects.all()
        events_list = [model_to_dict(event) for event in events]
        return JsonResponse(events_list, safe=False)

    elif request.method == "POST":
        data = json.loads(request.body)
        event = PlanningEvent.objects.create(
            subject=data.get('Subject'),
            start_time=data.get('StartTime'),
            end_time=data.get('EndTime'),
            employe_id=data.get('EmployeId'),
        )
        return JsonResponse(model_to_dict(event))

    elif request.method == "PUT":
        data = json.loads(request.body)
        event = PlanningEvent.objects.get(id=data.get('Id'))
        event.subject = data.get('Subject')
        event.start_time = data.get('StartTime')
        event.end_time = data.get('EndTime')
        event.employe_id = data.get('EmployeId')
        event.save()
        return JsonResponse(model_to_dict(event))

    elif request.method == "DELETE":
        data = json.loads(request.body)
        event = PlanningEvent.objects.get(id=data.get('Id'))
        event.delete()
        return JsonResponse({'message': 'Deleted'})

@login_required
#@permission_required('vitalia_app.can_view_event', raise_exception=True)
def event_list(request):
    users_in_groups = User.objects.filter(groups__name__in=["Chef des infirmiers", "Infirmier"])
    events = Evenement.objects.all()
    return render(request, 'vitalia_app/planning_infirmiers.html', {
        'users': users_in_groups,
        'events': events
    })

#@login_required
#@permission_required('vitalia_app.can_add_event', raise_exception=True)
# Vue pour créer un événement
def create_event(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EvenementForm()
    return render(request, 'event/create_event.html', {'form': form})

#@login_required
#@permission_required('vitalia_app.can_change_event', raise_exception=True)
# Vue pour modifier un événement
def edit_event(request, event_id):
    event = Evenement.objects.get(id=event_id)
    if request.method == 'POST':
        form = EvenementForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EvenementForm(instance=event)
    return render(request, 'event/edit_event.html', {'form': form})

#@login_required
#@permission_required('vitalia_app.can_delete_event', raise_exception=True)
# Vue pour supprimer un événement
def delete_event(request, event_id):
    event = Evenement.objects.get(id=event_id)
    event.delete()
    return redirect('event_list')

@login_required
def planning_individuel(request):
    user = request.user
    events = Evenement.objects.filter(employe=user)  
    return render(request, 'vitalia_app/planning_infirmier_individuel.html', {
        'events': events,
        'user_id': user.id
    })


@login_required
def planning_residents(request):
    residents = User.objects.filter(groups__name="Retraité")  
    events = Evenement.objects.all()
    return render(request, 'vitalia_app/planning_residents.html', {
        'residents': residents,
        'events': events
    })

@login_required
def planning_resident_individuel(request):
    resident_events = ResidentEvent.objects.filter(resident=request.user)
    return render(request, 'vitalia_app/planning_resident_individuel.html', {
        'resident_events': resident_events,
        'user_id': request.user.id
    })



def liste_chambres(request):
    q = request.GET.get('q', '')
    if q:
        chambres = Chambre.objects.filter(
            Q(numero__icontains=q) | 
            Q(resident__username__icontains=q) |
            Q(resident__first_name__icontains=q) |
            Q(resident__last_name__icontains=q)
        )
    else:
        chambres = Chambre.objects.all()
    return render(request, 'vitalia_app/liste_chambres.html', {'chambres': chambres})
