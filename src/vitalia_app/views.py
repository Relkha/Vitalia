import json
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, Case, When
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils.html import strip_tags
from django.forms.models import model_to_dict
from .forms import ContactForm, ConnexionForm, ChambreForm
from .models.MessageContact import MessageContact
from .models.Profil import Profil
from .models.Objets import ObjectPermission, ConnectedObject, PermissionType
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models.Alertes import Alert, Notification
from .models import Visit
from .models.Objets import ConnectedObject
from datetime import date, datetime, timedelta
from .models.Objets import ObjectPermission, ConnectedObject, PermissionType
from .models.planning_resident import PlanningEventResident
from .models.Chambre import Chambre
from .models.Evenement import Evenement
from .models.planning_infirmier import PlanningEventInfirmier
from .models.Alertes import Alert, Notification, AlertHistory
from .models.ObjectData import ObjectData
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer
from .forms import EvenementForm
import logging
import random
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import DossierMedical
from .forms import DossierMedicalForm


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
    chambre_id = request.GET.get('chambre')
    objets_connectes = []

    selected_chambre = None
    if chambre_id:
        try:
            selected_chambre = Chambre.objects.prefetch_related('objets_connectes').get(id=chambre_id)
            objets_connectes = selected_chambre.objets_connectes.all()
        except Chambre.DoesNotExist:
            selected_chambre = None

    return render(request, 'vitalia_app/surveillance.html', {
        'chambres': chambres,
        'selected_chambre': selected_chambre,
        'objets_connectes': objets_connectes,
    })



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


#Ajout


# === LISTE DES DOSSIERS MÉDICAUX ===

@login_required
def dossiers_medical(request):
    dossiers = DossierMedical.objects.select_related("patient", "infirmier").all()
    user_groups = [group.name.lower() for group in request.user.groups.all()]

    return render(request, "vitalia_app/dossiers_medical.html", {
        "patients": dossiers,
        "user_groups": user_groups,
    })


# === DOCUMENT PATIENT DÉTAIL ===

@login_required
@permission_required('vitalia_app.can_view_dossier', raise_exception=True)
def document_patient(request, pk):
    patient = get_object_or_404(DossierMedical, pk=pk)
    return render(request, 'vitalia_app/document_patient.html', {'patient': patient})


# === MODIFIER DOSSIER PATIENT ===

@login_required
@permission_required('vitalia_app.can_edit_own_consultation', raise_exception=True)
def modifier_patient(request, pk):
    dossier = get_object_or_404(DossierMedical, pk=pk)
    user_groups = [g.name for g in request.user.groups.all()]

    if request.user != dossier.infirmier and "Chef des infirmiers" not in user_groups:
        return HttpResponseForbidden("Vous ne pouvez modifier que vos propres dossiers.")

    form = DossierMedicalForm(request.POST or None, instance=dossier)

    if form.is_valid():
        form.save()
        return redirect('document_patient', pk=dossier.pk)

    return render(request, 'vitalia_app/dossier_patient_modifier.html', {'form': form})


# === ASSIGNER UN INFIRMIER ===

@login_required
@permission_required('vitalia_app.change_dossiermedical', raise_exception=True)
def assigner_infirmier(request, pk):
    dossier = get_object_or_404(DossierMedical, pk=pk)

    # Vérification des droits : chef ou responsable uniquement
    if not request.user.groups.filter(name__in=["Chef des infirmiers", "Responsable du site"]).exists():
        return HttpResponseForbidden("Accès refusé.")

    infirmiers = User.objects.filter(groups__name="Infirmier")

    if request.method == 'POST':
        infirmier_id = request.POST.get('infirmier')
        infirmier = get_object_or_404(User, id=infirmier_id)
        dossier.infirmier = infirmier
        dossier.save()
        return redirect('document_patient', pk=pk)

    return render(request, 'vitalia_app/assigner_infirmier.html', {
        'dossier': dossier,
        'infirmiers': infirmiers,
    })


# === EXPORTER UN DOSSIER EN PDF ===

@login_required
@permission_required('vitalia_app.can_view_dossier', raise_exception=True)
def export_dossier_pdf(request, pk):
    dossier = get_object_or_404(DossierMedical, pk=pk)
    template_path = 'vitalia_app/pdf_template.html'
    context = {'dossier': dossier}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dossier_{pk}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    return response


# === EXPORTER TOUS LES DOSSIERS EN UN SEUL PDF ===

@login_required
@permission_required('vitalia_app.can_view_dossier', raise_exception=True)
def export_all_dossiers_pdf(request):
    dossiers = DossierMedical.objects.select_related('patient', 'infirmier').all()
    template_path = 'vitalia_app/pdf_all_dossiers.html'
    context = {'dossiers': dossiers}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tous_les_dossiers.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    return response


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

            # Enregistrement dans la base de données
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
    visits = Visit.objects.filter(resident=request.user, status='validated')

    events = []

    # Debug : afficher le nombre d'événements
    print(f"Événements pour {request.user}: {resident_events.count()} events, {visits.count()} visits")

    for event in resident_events:
        events.append({
            'subject': event.subject,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'employe_id': request.user.id
        })

    for visit in visits:
        start_datetime = datetime.combine(visit.date, visit.time)
        end_datetime = start_datetime + timedelta(hours=1)

        events.append({
            'subject': 'Visite',
            'start_time': start_datetime,
            'end_time': end_datetime,
            'employe_id': request.user.id
        })

    # Debug : afficher les événements
    print(f"Total events to display: {len(events)}")
    for event in events:
        print(f"Event: {event}")

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



# Vue pour le tableau de bord des alertes
@login_required
def alertes_dashboard(request):
    # Récupérer toutes les alertes, triées par date et priorité
    alerts = Alert.objects.all().order_by('-priority', '-created_at')

    # Compter les alertes par priorité
    high_priority_count = Alert.objects.filter(priority='high', status__in=['new', 'in-progress']).count()
    medium_priority_count = Alert.objects.filter(priority='medium', status__in=['new', 'in-progress']).count()
    low_priority_count = Alert.objects.filter(priority='low', status__in=['new', 'in-progress']).count()
    total_alerts_count = alerts.count()

    # Pagination
    paginator = Paginator(alerts, 10)  # 10 alertes par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'alerts': page_obj,
        'high_priority_count': high_priority_count,
        'medium_priority_count': medium_priority_count,
        'low_priority_count': low_priority_count,
        'total_alerts_count': total_alerts_count
    }

    return render(request, 'vitalia_app/alertes_dashboard.html', context)


# API pour les détails d'une alerte
@login_required
def alert_details(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)

    # Construire l'objet de réponse
    data = {
        'id': alert.id,
        'title': alert.title,
        'description': alert.description,
        'created_at': alert.created_at.isoformat(),
        'priority': alert.priority,
        'priority_display': alert.get_priority_display(),
        'type': alert.type,
        'type_display': alert.get_type_display(),
        'status': alert.status,
        'status_display': alert.get_status_display(),
    }

    # Ajouter des informations sur l'appareil
    if alert.device:
        data['device'] = {
            'id': alert.device.id,
            'name': alert.device.name,
            'type': alert.device.type,
            'location': alert.device.location
        }

    # Ajouter des informations sur le résident
    if alert.resident:
        data['resident'] = {
            'id': alert.resident.user.id,
            'first_name': alert.resident.user.first_name,
            'last_name': alert.resident.user.last_name,
            'room_number': alert.resident.chambre.numero if hasattr(alert.resident, 'chambre') else None
        }

    # Ajouter l'historique de l'alerte
    data['history'] = []
    for entry in alert.alerthistory_set.all().order_by('-timestamp'):
        data['history'].append({
            'date': entry.timestamp.isoformat(),
            'action': entry.get_action_display(),
            'user': f"{entry.user.first_name} {entry.user.last_name}" if entry.user else "Système"
        })

    return JsonResponse(data)


# API pour prendre en charge une alerte
@login_required
def acknowledge_alert(request, alert_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    alert = get_object_or_404(Alert, id=alert_id)

    # Mettre à jour le statut de l'alerte
    alert.status = 'in-progress'
    alert.save()

    # Enregistrer l'action dans l'historique
    alert.alerthistory_set.create(
        user=request.user,
        action='acknowledge',
        details=f"Prise en charge par {request.user.first_name} {request.user.last_name}"
    )

    return JsonResponse({'success': True})


# API pour résoudre une alerte
@login_required
def resolve_alert(request, alert_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    alert = get_object_or_404(Alert, id=alert_id)

    # Mettre à jour le statut de l'alerte
    alert.status = 'resolved'
    alert.save()

    # Enregistrer l'action dans l'historique
    alert.alerthistory_set.create(
        user=request.user,
        action='resolve',
        details=f"Résolue par {request.user.first_name} {request.user.last_name}"
    )

    return JsonResponse({'success': True})


# Vue pour afficher les notifications de l'utilisateur
@login_required
def notifications(request):
    # Récupérer les notifications de l'utilisateur
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Marquer les notifications non lues comme lues
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)

    # Pagination
    paginator = Paginator(notifications, 15)  # 15 notifications par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'notifications': page_obj,
        'unread_count': unread_notifications.count()
    }

    return render(request, 'vitalia_app/notifications.html', context)


# API pour récupérer les notifications non lues
@login_required
def unread_notifications(request):
    # Récupérer les notifications non lues
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')

    # Construire la réponse
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
            'type': notification.type,
            'related_url': notification.related_url
        })

    return JsonResponse({'notifications': data, 'count': len(data)})


# Fonction pour créer une alerte et envoyer des notifications
def create_alert(title, description, priority, alert_type, device=None, resident=None):
    # Créer l'alerte
    alert = Alert.objects.create(
        title=title,
        description=description,
        priority=priority,
        type=alert_type,
        device=device,
        resident=resident,
        status='new'
    )

    # Déterminer quels groupes d'utilisateurs doivent être notifiés
    groups_to_notify = []

    if alert_type == 'medical':
        groups_to_notify.extend(['Infirmier', 'Chef des infirmiers', 'Aide-soignant'])
    elif alert_type == 'security':
        groups_to_notify.extend(['Responsable du site', 'Directeur'])
    elif alert_type == 'environmental':
        groups_to_notify.extend(['Ménage', 'Responsable du site'])
    elif alert_type == 'device':
        groups_to_notify.extend(['Responsable du site', 'Chef des infirmiers'])

    # Pour les alertes critiques, ajouter le directeur
    if priority == 'high':
        groups_to_notify.append('Directeur')

    # Récupérer tous les utilisateurs des groupes concernés
    user_ids = User.objects.filter(
        groups__name__in=groups_to_notify
    ).values_list('id', flat=True).distinct()

    users_to_notify = User.objects.filter(id__in=user_ids)

    # Créer des notifications pour chaque utilisateur
    for user in users_to_notify:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=description,
            type=alert_type,
            related_url=f"/alertes/details/{alert.id}/",
            is_read=False
        )

        # Envoyer un e-mail pour les alertes de haute priorité
        if priority == 'high' and user.email:
            send_alert_email(user, alert)

    return alert


# Fonction pour envoyer un e-mail d'alerte
def send_alert_email(user, alert):
    subject = f"ALERTE {alert.get_priority_display().upper()} : {alert.title}"

    # Préparer le contexte pour le template
    context = {
        'user': user,
        'alert': alert,
        'dashboard_url': f"{settings.SITE_URL}/alertes/",
        'alert_url': f"{settings.SITE_URL}/alertes/details/{alert.id}/"
    }

    # Rendre le template HTML
    html_message = render_to_string('email/alert_notification.html', context)
    plain_message = strip_tags(html_message)

    # Envoyer l'e-mail
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )




@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=["Directeur", "Responsable du site"]).exists())
def generate_test_alert(request):
    if request.method == 'POST':
        alert_type = request.POST.get('alert_type')
        priority = request.POST.get('alert_priority')
        title = request.POST.get('alert_title')
        description = request.POST.get('alert_description')

        # Créer l'alerte
        alert = Alert.objects.create(
            title=title,
            description=description,
            priority=priority,
            type=alert_type,
            status='new'
        )

        # Déterminer quels groupes d'utilisateurs doivent être notifiés
        groups_to_notify = []

        if alert_type == 'medical':
            groups_to_notify.extend(['Infirmier', 'Chef des infirmiers', 'Aide-soignant'])
        elif alert_type == 'security':
            groups_to_notify.extend(['Responsable du site', 'Directeur'])
        elif alert_type == 'environmental':
            groups_to_notify.extend(['Ménage', 'Responsable du site'])
        elif alert_type == 'device':
            groups_to_notify.extend(['Responsable du site', 'Chef des infirmiers'])

        # Pour les alertes critiques, ajouter le directeur
        if priority == 'high':
            groups_to_notify.append('Directeur')

        # Récupérer tous les utilisateurs des groupes concernés
        user_ids = User.objects.filter(
            groups__name__in=groups_to_notify
        ).values_list('id', flat=True).distinct()

        users_to_notify = User.objects.filter(id__in=user_ids)

        # Créer des notifications pour chaque utilisateur
        for user in users_to_notify:
            Notification.objects.create(
                user=user,
                title=title,
                message=description,
                type=alert_type,
                related_url=f"/alertes/",
                is_read=False
            )

        messages.success(request,
                         f"Alerte '{title}' créée avec succès et notifiée à {users_to_notify.count()} utilisateurs.")
        return redirect('generate_test_alert')

    return render(request, 'vitalia_app/generate_test_alert.html')




@login_required
def resident_connected_objects(request):
    user = request.user

    # Vérifier si l'utilisateur est un résident
    if not user.groups.filter(name="Retraité").exists():
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')

    # Vérifier si le résident est assigné à une chambre
    try:
        chambre = Chambre.objects.get(resident=user)
    except Chambre.DoesNotExist:
        messages.error(request, "Vous n'êtes pas assigné à une chambre.")
        return redirect('dashboard')

    # Récupérer les objets connectés de la chambre
    objets_connectes = ConnectedObject.objects.filter(room=chambre)

    # Préparer les données initiales pour l'affichage
    objects_data = {}

    for obj in objets_connectes:
        # Gérer spécifiquement les thermostats
        if obj.type == 'thermostat':
            try:
                # Récupérer directement depuis la base de données pour éviter tout problème de cache
                thermostat_data = ObjectData.objects.get(connected_object=obj)
                if thermostat_data.numeric_value is not None:
                    obj.current_temp = thermostat_data.numeric_value
                else:
                    obj.current_temp = 21  # Valeur par défaut
                    thermostat_data.numeric_value = 21
                    thermostat_data.save()
                print(f"Thermostat {obj.id}: température actuelle = {obj.current_temp}°C")
            except ObjectData.DoesNotExist:
                # Créer un enregistrement de données avec la valeur par défaut
                thermostat_data = ObjectData.objects.create(
                    connected_object=obj,
                    numeric_value=21
                )
                obj.current_temp = 21
                print(f"Nouveau thermostat {obj.id}: température par défaut = 21°C")

        # Récupérer les données des capteurs
        try:
            # Récupérer ou créer les données pour chaque type de capteur
            if obj.type == 'thermometer':
                obj_data, created = ObjectData.objects.get_or_create(connected_object=obj)
                if created or obj_data.numeric_value is None:
                    temp = round(20 + 5 * random.random(), 1)
                    obj_data.numeric_value = temp
                    obj_data.save()

                objects_data[obj.id] = {
                    'type': 'temperature',
                    'value': obj_data.numeric_value,
                    'unit': '°C',
                    'data': f"{obj_data.numeric_value}°C",
                    'icon': 'temperature'
                }

            elif obj.type == 'air_quality_sensor':
                obj_data, created = ObjectData.objects.get_or_create(connected_object=obj)
                if created or obj_data.numeric_value is None:
                    aqi = int(random.random() * 100)
                    obj_data.numeric_value = aqi
                    obj_data.save()

                aqi = obj_data.numeric_value
                quality = 'Bonne' if aqi < 50 else ('Moyenne' if aqi < 100 else 'Mauvaise')
                color = 'green' if aqi < 50 else ('orange' if aqi < 100 else 'red')

                objects_data[obj.id] = {
                    'type': 'air-quality',
                    'value': int(aqi),
                    'unit': 'AQI',
                    'data': f"{int(aqi)} AQI",
                    'quality': quality,
                    'color': color,
                    'icon': 'air-quality'
                }

            elif obj.type == 'door_sensor':
                obj_data, created = ObjectData.objects.get_or_create(connected_object=obj)
                if created or obj_data.boolean_value is None:
                    is_open = random.choice([True, False])
                    obj_data.boolean_value = is_open
                    obj_data.save()

                is_open = obj_data.boolean_value

                objects_data[obj.id] = {
                    'type': 'door',
                    'value': is_open,
                    'data': 'Ouverte' if is_open else 'Fermée',
                    'icon': 'door'
                }

            elif obj.type == 'presence_sensor':
                obj_data, created = ObjectData.objects.get_or_create(connected_object=obj)
                if created or obj_data.boolean_value is None:
                    presence = random.choice([True, False])
                    obj_data.boolean_value = presence
                    obj_data.save()

                presence = obj_data.boolean_value

                objects_data[obj.id] = {
                    'type': 'presence',
                    'value': presence,
                    'data': 'Présence détectée' if presence else 'Aucune présence',
                    'icon': 'presence'
                }

        except Exception as e:
            print(f"Erreur lors de la récupération des données pour l'objet {obj.id}: {e}")

    # Contexte à passer au template
    context = {
        'chambre': chambre,
        'objets_connectes': objets_connectes,
        'objects_data': json.dumps(objects_data)
    }

    return render(request, 'vitalia_app/resident_objects.html', context)


# Fonction d'exécution d'action sur un objet
def execute_action(obj, action, temp_value=None):
    """
    Exécute une action sur un objet connecté et sauvegarde les données.
    """
    result = {
        'object_id': obj.id,
        'object_name': obj.name,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'success': True
    }

    # Récupérer ou créer l'objet de données
    obj_data, created = ObjectData.objects.get_or_create(connected_object=obj)

    # Actions différentes selon le type d'objet
    if action == 'read':
        # Lecture de données existantes ou génération de nouvelles
        if obj.type == 'thermometer':
            # Si on n'a pas encore de données ou si elles sont vieilles, générer de nouvelles
            if created or obj_data.numeric_value is None:
                temperature = round(20 + 5 * random.random(), 1)
                obj_data.numeric_value = temperature
                obj_data.save()
            else:
                temperature = obj_data.numeric_value

            print(f"Thermomètre ID {obj.id}: température {temperature}, enregistré: {obj_data.numeric_value}")

            result['data'] = f"{temperature}°C"
            result['message'] = f"Température actuelle : {temperature}°C"
            result['value'] = temperature
            result['unit'] = '°C'
            result['icon'] = 'temperature'

        elif obj.type == 'air_quality_sensor':
            if created or obj_data.numeric_value is None:
                aqi = int(random.random() * 100)
                obj_data.numeric_value = aqi
                obj_data.save()
            else:
                aqi = obj_data.numeric_value

            result['data'] = f"{int(aqi)} AQI"
            result['message'] = f"Qualité de l'air : {int(aqi)} AQI"
            result['value'] = aqi
            result['unit'] = 'AQI'
            result['icon'] = 'air-quality'

            # Ajouter une interprétation de la qualité de l'air
            if aqi < 50:
                result['quality'] = 'Bonne'
                result['color'] = 'green'
            elif aqi < 100:
                result['quality'] = 'Moyenne'
                result['color'] = 'orange'
            else:
                result['quality'] = 'Mauvaise'
                result['color'] = 'red'

        elif obj.type == 'door_sensor':
            if created or obj_data.boolean_value is None:
                is_open = random.choice([True, False])
                obj_data.boolean_value = is_open
                obj_data.save()
            else:
                is_open = obj_data.boolean_value

            result['data'] = 'Ouverte' if is_open else 'Fermée'
            result['message'] = f"La porte est actuellement {result['data'].lower()}"
            result['value'] = is_open
            result['icon'] = 'door'

        elif obj.type == 'presence_sensor':
            if created or obj_data.boolean_value is None:
                presence_detected = random.choice([True, False])
                obj_data.boolean_value = presence_detected
                obj_data.save()
            else:
                presence_detected = obj_data.boolean_value

            result['data'] = 'Présence détectée' if presence_detected else 'Aucune présence'
            result['message'] = result['data']
            result['value'] = presence_detected
            result['icon'] = 'presence'

        else:
            result['data'] = "Données lues"
            result['message'] = f"Lecture des données de {obj.name} effectuée"

    elif action == 'power_on':
        obj.status = 'active'
        obj.save()

        if obj.type == 'lighting':
            result['message'] = f"Lumière allumée"
            result['icon'] = 'lightbulb-on'
        elif obj.type == 'thermostat':
            result['message'] = f"Chauffage allumé"
            result['icon'] = 'thermostat-on'
        elif obj.type == 'shutters':
            result['message'] = f"Volets ouverts"
            result['icon'] = 'shutters-open'
        else:
            result['message'] = f"{obj.name} a été allumé"

    elif action == 'power_off':
        obj.status = 'inactive'
        obj.save()

        if obj.type == 'lighting':
            result['message'] = f"Lumière éteinte"
            result['icon'] = 'lightbulb-off'
        elif obj.type == 'thermostat':
            result['message'] = f"Chauffage éteint"
            result['icon'] = 'thermostat-off'
        elif obj.type == 'shutters':
            result['message'] = f"Volets fermés"
            result['icon'] = 'shutters-closed'
        else:
            result['message'] = f"{obj.name} a été éteint"

    elif action == 'configure':
        if obj.type == 'thermostat':
            # Si une température est fournie, l'utiliser
            if temp_value is not None:
                try:
                    temperature = float(temp_value)
                    obj_data.numeric_value = temperature
                    obj_data.save()

                    # Log pour débogage
                    print(f"Thermostat ID {obj.id}: configuré à {temperature}°C, sauvegardé dans la BD")

                    result['message'] = f"Thermostat configuré à {temperature}°C"
                    result['icon'] = 'thermostat-config'
                    result['value'] = temperature
                    result['unit'] = '°C'
                except ValueError:
                    result['success'] = False
                    result['message'] = f"Valeur de température invalide"
            else:
                result['success'] = False
                result['message'] = f"Aucune température spécifiée"
        else:
            result['message'] = f"Configuration de {obj.name} effectuée"

    elif action == 'send_alert':
        # Simulation d'envoi d'alerte (interphone d'urgence)
        if obj.type == 'intercom':
            result['message'] = f"Alerte envoyée via l'interphone d'urgence"
            result['icon'] = 'alert'
            # Dans un cas réel, on pourrait créer une alerte dans le système
            # create_alert("Appel d'urgence", f"Un appel d'urgence a été lancé depuis la chambre {obj.room.numero}", "high", "security", obj, obj.room.resident)

    return result


# La vue pour contrôler un objet connecté
@login_required
@csrf_exempt
def control_object(request, object_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    # Récupérer l'objet connecté
    try:
        obj = ConnectedObject.objects.get(id=object_id)
    except ConnectedObject.DoesNotExist:
        return JsonResponse({'error': 'Objet non trouvé'}, status=404)

    # Vérifier si l'utilisateur est le résident de la chambre où se trouve l'objet
    if not obj.room.resident == request.user:
        return JsonResponse({'error': 'Vous n\'avez pas la permission de contrôler cet objet'}, status=403)

    # Récupérer le type d'action demandée
    action = request.POST.get('action')

    # Récupérer la température pour le thermostat si disponible
    temperature = request.POST.get('temperature')

    # Pour débogage
    if temperature:
        print(f"Température reçue pour l'objet {object_id}: {temperature}")

    # Vérifier si le type d'action est valide
    try:
        permission = PermissionType.objects.get(code=action)
    except PermissionType.DoesNotExist:
        return JsonResponse({'error': 'Action non valide'}, status=400)

    # Exécuter l'action sur l'objet
    result = execute_action(obj, action, temperature)

    return JsonResponse({'success': True, 'result': result})
@login_required
@group_required("Responsable du site", "Directeur")
def setup_connected_objects(request):
    """
    Crée les objets connectés pour toutes les chambres qui n'en ont pas encore
    """
    # Types d'objets à créer pour chaque chambre
    object_types = [
        {"name": "Thermostat intelligent", "type": "thermostat", "description": "Régle la température de la chambre"},
        {"name": "Éclairage intelligent", "type": "lighting",
         "description": "Permet d'ajuster la lumière de la chambre"},
        {"name": "Volets électriques", "type": "shutters", "description": "Ouvre et ferme les volets de la chambre"},
        {"name": "Capteur qualité de l'air", "type": "air_quality_sensor",
         "description": "Mesure la pollution, l'humidité et le CO2"},
        {"name": "Capteur de présence", "type": "presence_sensor",
         "description": "Détecte les mouvements dans la chambre"},
        {"name": "Capteur ouverture de porte", "type": "door_sensor",
         "description": "Détecte si une porte est ouverte"},
        {"name": "Thermomètre", "type": "thermometer", "description": "Capteur de température"}
    ]

    # Récupérer toutes les chambres
    chambres = Chambre.objects.all()

    # Compteurs pour le rapport
    total_objets = 0
    nouvelles_chambres = 0

    for chambre in chambres:
        # Vérifier si la chambre a déjà des objets
        existing_objects = ConnectedObject.objects.filter(room=chambre)
        existing_types = set(obj.type for obj in existing_objects)

        has_new_objects = False

        # Créer les objets manquants pour cette chambre
        for obj_type in object_types:
            if obj_type["type"] not in existing_types:
                ConnectedObject.objects.create(
                    name=f"{obj_type['name']} - Chambre {chambre.numero}",
                    type=obj_type["type"],
                    description=obj_type["description"],
                    room=chambre,
                    status="active"
                )
                total_objets += 1
                has_new_objects = True

        if has_new_objects:
            nouvelles_chambres += 1

    # Créer les permissions pour le groupe Retraité
    retraite_group = Group.objects.get(name="Retraité")

    # Définir quelles actions sont permises sur quels types d'objets
    permission_mapping = {
        "thermostat": ["read", "power_on", "power_off", "configure"],
        "lighting": ["power_on", "power_off", "configure"],
        "shutters": ["power_on", "power_off"],
        "air_quality_sensor": ["read"],
        "presence_sensor": ["read"],
        "door_sensor": ["read"],
        "thermometer": ["read"]
    }

    for obj in ConnectedObject.objects.all():
        # Vérifier si une permission existe déjà
        if not ObjectPermission.objects.filter(connected_object=obj, group=retraite_group).exists():
            # Créer la permission
            perm = ObjectPermission.objects.create(
                connected_object=obj,
                group=retraite_group
            )

            # Ajouter les types de permission appropriés
            if obj.type in permission_mapping:
                for perm_code in permission_mapping[obj.type]:
                    try:
                        perm_type = PermissionType.objects.get(code=perm_code)
                        perm.permissions.add(perm_type)
                    except PermissionType.DoesNotExist:
                        pass

    messages.success(request, f"{total_objets} objets connectés ont été créés pour {nouvelles_chambres} chambres.")
    return redirect('liste_chambres')