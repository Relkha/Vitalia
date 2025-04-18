from django.core.management.base import BaseCommand
from ...models.Objets import PermissionType

class Command(BaseCommand):
    help = "Crée les permissions types pour les objets connectés"

    def handle(self, *args, **kwargs):
        permissions = [
            {"code": "read", "label": "Lecture des données"},
            {"code": "send_alert", "label": "Envoyer une alerte"},
            {"code": "view_logs", "label": "Voir les enregistrements / logs"},
            {"code": "power_on", "label": "Allumer l'objet"},
            {"code": "power_off", "label": "Éteindre l'objet"},
            {"code": "configure", "label": "Configurer les paramètres"},
        ]

        for perm in permissions:
            obj, created = PermissionType.objects.get_or_create(
                code=perm["code"],
                defaults={"label": perm["label"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Créé : {obj.label}"))
            else:
                self.stdout.write(f"Déjà existant : {obj.label}")
