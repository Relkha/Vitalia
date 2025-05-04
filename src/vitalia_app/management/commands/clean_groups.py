from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Fusionne les groupes en doublon dans les noms officiels"

    def handle(self, *args, **kwargs):
        corrections = {
            "administrateur": "Responsable du site",
            "directeur": "Directeur",
            "chef infirmier": "Chef des infirmiers",
            "infirmier": "Infirmier",
            "aide soignant": "Aide-soignant",
            "retraité": "Retraité",
        }

        for wrong_name, correct_name in corrections.items():
            try:
                wrong_group = Group.objects.get(name=wrong_name)
                correct_group = Group.objects.get(name=correct_name)
            except Group.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠️ Le groupe '{wrong_name}' ou '{correct_name}' n'existe pas."))
                continue

            # Transférer les permissions
            for perm in wrong_group.permissions.all():
                correct_group.permissions.add(perm)

            # Transférer les utilisateurs
            for user in wrong_group.user_set.all():
                user.groups.add(correct_group)
                user.groups.remove(wrong_group)

            # Supprimer le doublon
            wrong_group.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ Fusion de '{wrong_name}' vers '{correct_name}' terminée."))

        self.stdout.write(self.style.SUCCESS("🎯 Nettoyage des groupes terminé."))
