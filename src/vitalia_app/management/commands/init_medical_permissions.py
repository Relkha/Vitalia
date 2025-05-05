from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from vitalia_app.models import DossierMedical


class Command(BaseCommand):
    help = "Attribue les permissions liées aux dossiers médicaux aux bons groupes"

    def handle(self, *args, **kwargs):
        roles = {
            "Infirmier": ["add_dossiermedical", "change_dossiermedical", "can_view_dossier"],
            "Chef des infirmiers": ["add_dossiermedical", "change_dossiermedical", "can_view_dossier"],
            "Aide-soignant": ["can_view_dossier"],
            "Directeur": ["can_view_dossier"],
            "Responsable du site": ["can_view_dossier"],
            "Retraité": ["can_view_dossier"]
        }

        content_type = ContentType.objects.get_for_model(DossierMedical)

        for role, permissions in roles.items():
            group, _ = Group.objects.get_or_create(name=role)
            perms = []

            for codename in permissions:
                try:
                    perm = Permission.objects.get(codename=codename, content_type=content_type)
                    perms.append(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"⚠️ Permission introuvable : '{codename}'"))

            group.permissions.set(perms, clear=False)
            self.stdout.write(f"🔐 {len(perms)} permission(s) mises à jour pour le groupe '{role}'.")

        self.stdout.write(self.style.SUCCESS("✅ Permissions médicales attribuées avec succès."))
