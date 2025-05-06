from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from ...models.Objets import ConnectedObject, ObjectPermission, PermissionType
from ...models.Chambre import Chambre


class Command(BaseCommand):
    help = "Duplique les objets connectés dans toutes les chambres et assigne les permissions"

    def handle(self, *args, **kwargs):
        # Assurez-vous que toutes les permissions nécessaires existent
        permission_types = [
            {"code": "read", "label": "Lecture des données"},
            {"code": "send_alert", "label": "Envoyer une alerte"},
            {"code": "view_logs", "label": "Voir les enregistrements / logs"},
            {"code": "power_on", "label": "Allumer l'objet"},
            {"code": "power_off", "label": "Éteindre l'objet"},
            {"code": "configure", "label": "Configurer les paramètres"},
        ]

        # Créer les types de permissions s'ils n'existent pas
        perm_map = {}
        for perm_data in permission_types:
            perm, created = PermissionType.objects.get_or_create(
                code=perm_data["code"],
                defaults={"label": perm_data["label"]}
            )
            perm_map[perm_data["code"]] = perm
            if created:
                self.stdout.write(f"Créé le type de permission: {perm.label}")

        # Définition des types d'objets
        object_types = [
            {
                "name": "Thermostat intelligent",
                "type": "thermostat",
                "description": "Régule la température de la chambre",
                "groups": ["Retraité", "Directeur"],
                "permissions": {
                    "Retraité": ["read", "power_on", "power_off", "configure"],
                    "Directeur": ["read", "power_on", "power_off", "configure", "view_logs"]
                }
            },
            {
                "name": "Éclairage intelligent",
                "type": "lighting",
                "description": "Permet d'ajuster la lumière de la chambre",
                "groups": ["Retraité", "Directeur", "Ménage"],
                "permissions": {
                    "Retraité": ["power_on", "power_off", "configure"],
                    "Directeur": ["power_on", "power_off", "configure", "view_logs"],
                    "Ménage": ["power_on", "power_off"]
                }
            },
            {
                "name": "Volets électriques",
                "type": "shutters",
                "description": "Ouvre et ferme les volets de la chambre",
                "groups": ["Retraité", "Directeur"],
                "permissions": {
                    "Retraité": ["power_on", "power_off"],
                    "Directeur": ["power_on", "power_off", "view_logs"]
                }
            },
            {
                "name": "Capteur qualité de l'air",
                "type": "air_quality_sensor",
                "description": "Mesure la pollution, l'humidité et le CO2",
                "groups": ["Retraité", "Directeur", "Ménage", "Infirmier"],
                "permissions": {
                    "Retraité": ["read"],
                    "Directeur": ["read", "view_logs"],
                    "Ménage": ["read"],
                    "Infirmier": ["read"]
                }
            },
            {
                "name": "Capteur de présence",
                "type": "presence_sensor",
                "description": "Détecte les mouvements dans la chambre",
                "groups": ["Retraité", "Directeur", "Infirmier", "Chef des infirmiers"],
                "permissions": {
                    "Retraité": ["read"],
                    "Directeur": ["read", "view_logs"],
                    "Infirmier": ["read"],
                    "Chef des infirmiers": ["read", "view_logs"]
                }
            },
            {
                "name": "Capteur ouverture de porte",
                "type": "door_sensor",
                "description": "Détecte si une porte est ouverte",
                "groups": ["Retraité", "Directeur", "Infirmier"],
                "permissions": {
                    "Retraité": ["read"],
                    "Directeur": ["read", "send_alert", "view_logs"],
                    "Infirmier": ["read"]
                }
            },
            {
                "name": "Thermomètre",
                "type": "thermometer",
                "description": "Capteur de température",
                "groups": ["Retraité", "Directeur", "Infirmier"],
                "permissions": {
                    "Retraité": ["read"],
                    "Directeur": ["read", "view_logs"],
                    "Infirmier": ["read"]
                }
            },
            {
                "name": "Interphone d'urgence",
                "type": "intercom",
                "description": "Permet d'appeler un infirmier en cas d'urgence",
                "groups": ["Retraité", "Directeur", "Infirmier", "Chef des infirmiers"],
                "permissions": {
                    "Retraité": ["send_alert"],
                    "Directeur": ["send_alert", "view_logs"],
                    "Infirmier": ["send_alert"],
                    "Chef des infirmiers": ["send_alert", "view_logs"]
                }
            }
        ]

        # Récupérer toutes les chambres
        chambres = Chambre.objects.all()
        self.stdout.write(f"Création des objets pour {chambres.count()} chambres")

        # Compteurs
        total_created = 0

        # Pour chaque chambre, créer tous les types d'objets
        for chambre in chambres:
            # Vérifier quels types d'objets existent déjà pour cette chambre
            existing_objects = ConnectedObject.objects.filter(room=chambre)
            existing_types = {obj.type for obj in existing_objects}

            for obj_type in object_types:
                # Si ce type d'objet n'existe pas encore dans cette chambre, le créer
                if obj_type["type"] not in existing_types:
                    obj_name = f"{obj_type['name']} - Chambre {chambre.numero}"
                    obj = ConnectedObject.objects.create(
                        name=obj_name,
                        type=obj_type["type"],
                        description=obj_type["description"],
                        room=chambre,
                        status="active"
                    )
                    total_created += 1
                    self.stdout.write(f"Créé : {obj_name}")

                    # Assigner les permissions pour chaque groupe
                    for group_name, perms in obj_type["permissions"].items():
                        try:
                            group = Group.objects.get(name=group_name)
                            perm_obj, created = ObjectPermission.objects.get_or_create(
                                connected_object=obj,
                                group=group
                            )
                            # Ajouter les permissions pour ce groupe
                            for perm_code in perms:
                                perm_obj.permissions.add(perm_map[perm_code])
                            self.stdout.write(f"  ↳ Permissions {group_name}: {', '.join(perms)}")
                        except Group.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Le groupe {group_name} n'existe pas"))

        self.stdout.write(self.style.SUCCESS(f"Terminé! {total_created} objets créés"))