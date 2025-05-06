from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vitalia_app.models import DossierMedical
from django.utils import timezone

class Command(BaseCommand):
    help = "Crée automatiquement des dossiers médicaux pour les utilisateurs existants sans dossier"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        count = 0

        for user in users:
            if not DossierMedical.objects.filter(patient=user).exists():
                DossierMedical.objects.create(
                    patient=user,
                    infirmier=None,
                    etat="État initial",
                    date_entree=timezone.now()
                )
                self.stdout.write(f"✅ Dossier médical créé pour {user.username}")
                count += 1

        if count == 0:
            self.stdout.write("📭 Aucun nouveau dossier à créer.")
        else:
            self.stdout.write(f"🎯 {count} dossier(s) médical(aux) créé(s).")
