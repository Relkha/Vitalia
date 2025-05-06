# vitalia_app/initial_setup.py
from django.contrib.auth.models import User
from vitalia_app.models import DossierMedical
from django.utils import timezone

def create_missing_dossiers():
    users = User.objects.all()
    count = 0

    for user in users:
        if user.first_name and user.last_name:
            if not DossierMedical.objects.filter(patient=user).exists():
                DossierMedical.objects.create(
                    patient=user,
                    infirmier=None,
                    etat="État initial",
                    date_entree=timezone.now()
                )
                print(f"✅ Dossier médical créé pour {user.username}")
                count += 1

    if count == 0:
        print("📭 Aucun nouveau dossier à créer.")
    else:
        print(f"🎯 {count} dossier(s) médical(aux) créé(s).")

