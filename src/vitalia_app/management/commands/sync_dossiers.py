from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from vitalia_app.models import DossierMedical

class Command(BaseCommand):
    help = "Crée les dossiers médicaux manquants pour les utilisateurs du groupe 'Retraité'"

    def handle(self, *args, **kwargs):
        groupe = Group.objects.get(name="Retraité")
        users = User.objects.filter(groups=groupe)
        count_created = 0

        for user in users:
            obj, created = DossierMedical.objects.get_or_create(patient=user)
            if created:
                count_created += 1
                self.stdout.write(f"✅ Dossier créé pour {user.username}")
            else:
                self.stdout.write(f"ℹ️ Dossier déjà existant pour {user.username}")

        self.stdout.write(self.style.SUCCESS(f"🎯 {count_created} nouveau(x) dossier(s) médical(aux) créé(s)."))
