from django.apps import AppConfig
import threading

class VitaliaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vitalia_app'

    def ready(self):
        from .initial_setup import create_missing_dossiers
        create_missing_dossiers()
        from django.contrib.auth import get_user_model
        from .models import DossierMedical
        from django.db.utils import OperationalError
        from django.core.exceptions import AppRegistryNotReady

        def create_dossiers():
            try:
                User = get_user_model()
                created = 0
                for user in User.objects.all():
                    if user.first_name.strip() and user.last_name.strip():
                        if not DossierMedical.objects.filter(patient=user).exists():
                            DossierMedical.objects.create(patient=user)
                            created += 1
                print(f"🩺 {created} dossier(s) médical(aux) créés au démarrage.")
            except (OperationalError, AppRegistryNotReady):
                print("⚠️ La base de données n'est pas encore prête.")

        # Pour ne pas bloquer le démarrage de Django
        threading.Thread(target=create_dossiers).start()




