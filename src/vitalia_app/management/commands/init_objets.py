from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from ...models.Objets import ConnectedObject, ObjectPermission, PermissionType

class Command(BaseCommand):
    help = "Crée les objets connectés et assigne les permissions aux groupes"

    def handle(self, *args, **kwargs):
        perm_map = {
            "read": PermissionType.objects.get(code="read"),
            "send_alert": PermissionType.objects.get(code="send_alert"),
            "view_logs": PermissionType.objects.get(code="view_logs"),
            "power_on": PermissionType.objects.get(code="power_on"),
            "power_off": PermissionType.objects.get(code="power_off"),
            "configure": PermissionType.objects.get(code="configure"),
        }

        objets = [
            {
                "name": "Bracelet connecté",
                "type": "bracelet",
                "description": "Mesure la fréquence cardiaque, la température et détecte les chutes",
                "groups": ["Directeur", "Chef des infirmiers", "Infirmier", "Aide-soignant", "Retraité"],
                "permissions": ["read", "send_alert"]
            },
            {
                "name": "Capteur de présence",
                "type": "presence_sensor",
                "description": "Détecte si un résident est dans sa chambre ou hors de son lit",
                "groups": ["Directeur", "Chef des infirmiers", "Réceptionniste"],
                "permissions": ["read", "send_alert"]
            },
            {
                "name": "Caméra de surveillance",
                "type": "camera",
                "description": "Surveille les entrées/sorties et les couloirs",
                "groups": ["Directeur", "Responsable du site", "Réceptionniste"],
                "permissions": ["read", "view_logs"]
            },
            {
                "name": "Capteur ouverture de porte",
                "type": "door_sensor",
                "description": "Détecte si une porte est ouverte hors des horaires",
                "groups": ["Directeur", "Chef des infirmiers"],
                "permissions": ["send_alert"]
            },
            {
                "name": "Interphone urgence",
                "type": "intercom",
                "description": "Permet à un résident d’appeler un infirmier",
                "groups": ["Directeur", "Infirmier", "Aide-soignant", "Retraité"],
                "permissions": ["send_alert"]
            },
            {
                "name": "Thermostat intelligent",
                "type": "thermostat",
                "description": "Régule la température des chambres",
                "groups": ["Directeur", "Retraité", "Infirmier", "Ménage"],
                "permissions": ["read", "configure"]
            },
            {
                "name": "Éclairage intelligent",
                "type": "lighting",
                "description": "Permet d’ajuster la lumière des chambres",
                "groups": ["Directeur", "Retraité", "Ménage"],
                "permissions": ["configure"]
            },
            {
                "name": "Volets électriques",
                "type": "shutters",
                "description": "Ouvre et ferme les volets des chambres",
                "groups": ["Directeur", "Retraité"],
                "permissions": ["configure"]
            },
            {
                "name": "Capteur qualité de l’air",
                "type": "air_sensor",
                "description": "Mesure la pollution, l’humidité et le CO2",
                "groups": ["Directeur", "Ménage"],
                "permissions": ["send_alert"]
            }
        ]

        for obj_data in objets:
            obj, created = ConnectedObject.objects.get_or_create(
                name=obj_data["name"],
                defaults={
                    "type": obj_data["type"],
                    "description": obj_data["description"],
                    "status": "active",
                }
            )
            self.stdout.write(self.style.SUCCESS(f"{'Créé' if created else 'Déjà existant'} : {obj.name}"))

            for group_name in obj_data["groups"]:
                group = Group.objects.get(name=group_name)
                obj_perm, _ = ObjectPermission.objects.get_or_create(connected_object=obj, group=group)
                obj_perm.permissions.set([perm_map[p] for p in obj_data["permissions"]])
                self.stdout.write(f"  ↳ {group.name} : {', '.join(obj_data['permissions'])}")
