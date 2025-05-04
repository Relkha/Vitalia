import json
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Q, Case, When
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.forms.models import model_to_dict
from .forms import ContactForm, ConnexionForm, ChambreForm
from .models.MessageContact import MessageContact
from .models.Profil import Profil
from .models.Objets import ObjectPermission, ConnectedObject, PermissionType
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Visit
from .models.Objets import ConnectedObject
from datetime import date, datetime, timedelta
from .models.Objets import ObjectPermission, ConnectedObject, PermissionType
from .models.planning_resident import PlanningEventResident
from .models.Chambre import Chambre
from .models.Evenement import Evenement
from .models.planning_infirmier import PlanningEventInfirmier
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer
from .forms import EvenementForm
import logging

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
        'objets_connectes': objets_connectes
    })


@login_required
def reservation_visite(request):
    if not hasattr(request.user, 'profil') or request.user.profil.get_role() not in ['Visiteur des résidents', 'Retraité', 'Réceptionniste']:
        return redirect('/')

    if request.method == 'POST':
        Visit.objects.create(
            resident=request.user,
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            status='validated'
        )
        return redirect('reservation_visite')

    visites = Visit.objects.filter(resident=request.user).order_by('-date', '-time')
    today = date.today()

    return render(request, 'reservation_visite.html', {'visites': visites, 'today': today})


logger = logging.getLogger(__name__)

#groups permissions
def group_required(*group_names):
    def in_groups(user):
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if user.groups.filter(name__in=group_names).exists():
                return True
        raise PermissionDenied
    return user_passes_test(in_groups)


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
    message_type = request.GET.get('type', '')
    prefilled = {}

    if message_type == "creation_compte":
        prefilled = {
            "objet": "Demande de création de compte",
            "message": (
                "Bonjour,\n\n"
                "Je souhaite créer un compte utilisateur pour accéder à la plateforme Vitalia.\n"
                "Merci de bien vouloir prendre en compte ma demande.\n\n"
                "Informations à compléter :\n"
                "- Prénom :\n"
                "- Nom :\n"
                "- Rôle souhaité (ex : Infirmier, Retraité, etc.) :\n"
                "- Email :\n"
                "- Numéro de téléphone :\n"
            )
        }

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
        form = ContactForm(initial=prefilled)
    return render(request, "contact.html", {'form': form})

def message_admin(request):
    messages = MessageContact.objects.order_by('-date_envoi')
    # Ajoute un champ supplémentaire pour détecter les messages "demande de création de compte"
    for msg in messages:
        msg.type_message = "creation_compte" if "création de compte" in msg.objet.lower() else "autre"
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
@login_required
def planning_events_api(request):
    try:
        # Gérer la lecture des événements (peut venir de GET ou POST avec params)
        if request.method == "GET" or (request.method == "POST" and "action" not in json.loads(request.body)):
            if request.method == "POST":
                data = json.loads(request.body)
                # print(f"POST request for reading events: {data}")
                start_date = data.get('StartDate')
                end_date = data.get('EndDate')
                employe_id = data.get('EmployeId')
            else:
                start_date = request.GET.get('StartTime') or request.GET.get('StartDate')
                end_date = request.GET.get('EndTime') or request.GET.get('EndDate')
                employe_id = request.GET.get('EmployeId')

            # print(f"Reading events: StartDate={start_date}, EndDate={end_date}, EmployeId={employe_id}")

            # Récupérer tous les événements
            events = PlanningEventInfirmier.objects.all()

            if employe_id:
                events = events.filter(employe__id=employe_id)

            if start_date and end_date:
                # Convertir les dates selon le format fourni
                try:
                    if 'Z' in start_date:  # Format ISO avec timezone
                        start = parse_datetime(start_date)
                        end = parse_datetime(end_date)
                    else:
                        start = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                        end = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

                    events = events.filter(start_time__gte=start, end_time__lte=end)
                except Exception as e:
                    # print(f"Error parsing dates: {e}")
                    pass

            events_list = [
                {
                    'id': event.id,
                    'subject': event.subject,
                    'start_time': event.start_time.isoformat(),
                    'end_time': event.end_time.isoformat(),
                    'EmployeId': event.employe.id if event.employe else None,
                    'IsAllDay': False
                }
                for event in events
            ]

            # print(f"Returning {len(events_list)} events: {events_list}")
            return JsonResponse(events_list, safe=False)

        # création/modifs/delete
        elif request.method == "POST" and "action" in json.loads(request.body):
            data = json.loads(request.body)
            # Pour débogage
            # print("DATA REÇUE:", data)

            if data.get('action') == 'batch':
                response_data = {'added': [], 'changed': [], 'deleted': []}

                # Traiter les ajouts
                if 'added' in data and len(data['added']) > 0:
                    for item in data['added']:
                        subject = item.get('subject')
                        start_time_raw = item.get('start_time')
                        end_time_raw = item.get('end_time')
                        employe_id = item.get('EmployeId')

                        if not all([subject, start_time_raw, end_time_raw]):
                            continue

                        start_time = parse_datetime(start_time_raw)
                        end_time = parse_datetime(end_time_raw)

                        if not start_time or not end_time:
                            continue

                        # Récupérer l'employé selon l'ID fourni ou utiliser l'utilisateur courant
                        employe = User.objects.get(id=employe_id) if employe_id else request.user

                        # Création de l'événement
                        event = PlanningEventInfirmier.objects.create(
                            subject=subject,
                            start_time=start_time,
                            end_time=end_time,
                            employe=employe,
                            title=subject,
                            description=f"Événement créé le {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        )

                        # print(f"Event created: ID={event.id}, Subject={event.subject}, Start={event.start_time}")

                        response_data['added'].append({
                            'id': event.id,
                            'subject': event.subject,
                            'start_time': event.start_time.isoformat(),
                            'end_time': event.end_time.isoformat(),
                            'EmployeId': event.employe.id,
                            'IsAllDay': False
                        })

                # Traiter les modifications
                if 'changed' in data and len(data['changed']) > 0:
                    for item in data['changed']:
                        event_id = item.get('id')
                        if not event_id:
                            continue

                        try:
                            event = PlanningEventInfirmier.objects.get(id=event_id)

                            if 'subject' in item:
                                event.subject = item['subject']
                                event.title = item['subject']

                            if 'start_time' in item:
                                event.start_time = parse_datetime(item['start_time'])

                            if 'end_time' in item:
                                event.end_time = parse_datetime(item['end_time'])

                            if 'EmployeId' in item:
                                event.employe = User.objects.get(id=item['EmployeId'])

                            event.save()

                            response_data['changed'].append({
                                'id': event.id,
                                'subject': event.subject,
                                'start_time': event.start_time.isoformat(),
                                'end_time': event.end_time.isoformat(),
                                'EmployeId': event.employe.id,
                                'IsAllDay': False
                            })
                        except PlanningEventInfirmier.DoesNotExist:
                            continue

                # Traiter les suppressions
                if 'deleted' in data and len(data['deleted']) > 0:
                    for item in data['deleted']:
                        event_id = item.get('id')
                        if not event_id:
                            continue

                        try:
                            event = PlanningEventInfirmier.objects.get(id=event_id)
                            event_data = {
                                'id': event.id,
                                'subject': event.subject,
                                'start_time': event.start_time.isoformat(),
                                'end_time': event.end_time.isoformat(),
                                'EmployeId': event.employe.id if event.employe else None,
                                'IsAllDay': False
                            }
                            event.delete()
                            response_data['deleted'].append(event_data)
                        except PlanningEventInfirmier.DoesNotExist:
                            continue

                return JsonResponse(response_data)

            return JsonResponse({'error': 'Action non supportée'}, status=400)

    except Exception as e:
        # logger.error(f"Error in planning_events_api: {e}")
        # print(f"Exception in planning_events_api: {str(e)}")
        # import traceback
        # traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@group_required("Chef des infirmiers", "Responsable du site", "Directeur")
def event_list(request):
    users_in_groups = User.objects.filter(groups__name__in=["Chef des infirmiers", "Infirmier"])
    events = PlanningEventInfirmier.objects.all()
    return render(request, 'vitalia_app/planning_infirmiers.html', {
        'users': users_in_groups,
        'events': events
    })

'''
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
    event = PlanningEventInfirmier.objects.get(id=event_id)
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
    event = PlanningEventInfirmier.objects.get(id=event_id)
    event.delete()
    return redirect('event_list')
'''

@login_required
@group_required("Infirmier", "Aide-soignant", "Ménage")
def planning_individuel(request):
    user = request.user
    events = PlanningEventInfirmier.objects.filter(employe=user)
    return render(request, 'vitalia_app/planning_infirmier_individuel.html', {
        'events': events,
        'user_id': user.id
    })


@login_required
@group_required("Responsable du site", "Chef des infirmiers", "Infirmier", "Directeur")
def planning_residents(request):
    residents = User.objects.filter(groups__name="Retraité")

    # Récupérer tous les événements
    events = []

    evenements = Evenement.objects.all()
    for event in evenements:
        if hasattr(event, 'resident'):
            events.append({
                'subject': event.subject,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'resident_id': event.resident.id
            })

    # Récupérer toutes les visites des résidents
    visits = Visit.objects.filter(status='validated', resident__groups__name="Retraité")
    for visit in visits:
        start_datetime = datetime.combine(visit.date, visit.time)
        end_datetime = start_datetime + timedelta(hours=1)

        events.append({
            'subject': 'Visite',
            'start_time': start_datetime,
            'end_time': end_datetime,
            'resident_id': visit.resident.id
        })

    colors = ['#ffaa00', '#00bbff', '#ff5566', '#33cc33', '#9966ff', '#ff9900']
    for i, resident in enumerate(residents):
        resident.color = colors[i % len(colors)]

    return render(request, 'vitalia_app/planning_residents.html', {
        'residents': residents,
        'events': events
    })

@login_required
@group_required("Retraité")
def planning_resident_individuel(request):
    resident_events = PlanningEventResident.objects.filter(resident=request.user)

    # Récupérer les visites pour ce résident
    visits = Visit.objects.filter(resident=request.user, status='validated')

    events = []

    for event in resident_events:
        events.append({
            'subject': event.subject,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'employe_id': request.user.id
        })

    for visit in visits:
        start_datetime = datetime.combine(visit.date, visit.time)
        # Supposons que chaque visite dure 1 heure
        end_datetime = start_datetime + timedelta(hours=1)

        events.append({
            'subject': 'Visite',
            'start_time': start_datetime,
            'end_time': end_datetime,
            'employe_id': request.user.id
        })

    return render(request, 'vitalia_app/planning_resident_individuel.html', {
        'events': events,
        'user_id': request.user.id
    })


@login_required
@group_required("Responsable du site", "Directeur", "Chef des infirmiers", "Infirmier")
def modifier_chambre(request, chambre_id):
    chambre = get_object_or_404(Chambre, id=chambre_id)

    if request.method == 'POST':
        form = ChambreForm(request.POST, instance=chambre)
        if form.is_valid():
            form.save()
            return redirect('liste_chambres')
    else:
        form = ChambreForm(instance=chambre)

    context = {
        'form': form,
        'chambre': chambre,
    }
    return render(request, 'vitalia_app/modifier_chambre.html', context)

'''
@login_required
def voir_chambre(request, chambre_id):
    chambre = get_object_or_404(Chambre, id=chambre_id)
    context = {
        'chambre': chambre,
    }
    return render(request, 'vitalia_app/voir_chambre.html', context)
'''


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
    #Tri par statut de chambres
    chambres = chambres.order_by(
        Case(
            When(statut='OCCUPE', then=0),
            When(statut='RESERVE', then=1),
            When(statut='LIBRE', then=2),
            default=3
        ),
        'numero'
    )

    user = request.user
    role = user.groups.first().name if user.groups.exists() else "Aucun"

    context = {
        'chambres': chambres,
        'is_admin': role == "Responsable du site",
        'is_directeur': role == "Directeur",
        'is_chef_infirmier': role == "Chef des infirmiers",
        'is_infirmier': role == "Infirmier",
    }

    return render(request, 'vitalia_app/liste_chambres.html', context)