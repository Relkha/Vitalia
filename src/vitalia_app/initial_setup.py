'''
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models.planning_infirmier import PlanningEventInfirmier
from .models.Evenement import Evenement

def create_default_groups():
    # Création des groupes
    group_names = [
        "Responsable du site",
        "Directeur",
        "Chef des infirmiers",
        "Infirmier",
        "Aide-soignant",
        "Ménage",
        "Réceptionniste",
        "Retraité",
        "Visiteur du site",
        "Visiteur des résidents"
    ]

    # ContentType du modèle Evenement
    evenement_ct = ContentType.objects.get_for_model(Evenement)

    # Création des permissions 
    view_own_perm, _ = Permission.objects.get_or_create(
        codename='view_own_evenement',
        name='Peut voir uniquement ses propres événements',
        content_type=evenement_ct
    )

    # Création de la permission `can_view_timeline` si elle n'existe pas
    can_view_timeline_perm, _ = Permission.objects.get_or_create(
        codename='can_view_timeline',
        name='Peut voir le calendrier des événements',
        content_type=evenement_ct
    )

    # Attribution des permissions
    group_permissions = {
        "Directeur": ["view_evenement", "change_evenement"],
        "Responsable du site": ["view_evenement", "change_evenement"],
        "Chef des infirmiers": ["view_evenement", "change_evenement", "can_view_timeline"],
        "Infirmier": ["view_own_evenement"],
        # Autres permissions des autres groupes
    }

    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)
        if created:
            print(f"Groupe '{name}' créé.")
        else:
            print(f"Groupe '{name}' déjà existant.")

        perms = group_permissions.get(name, [])
        for perm_codename in perms:
            try:
                perm = Permission.objects.get(codename=perm_codename, content_type=evenement_ct)
                group.permissions.add(perm)
                print(f"  → Permission '{perm_codename}' ajoutée au groupe '{name}'")
            except Permission.DoesNotExist:
                print(f"  !! Permission '{perm_codename}' introuvable pour le groupe '{name}'")
'''