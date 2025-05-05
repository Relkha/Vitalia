from django.core.management.base import BaseCommand
from ...alerte_utils import check_bracelet_alerts, check_air_quality_sensors, check_door_sensors
from ...models.Objets import ConnectedObject


class Command(BaseCommand):
    help = 'Vérifie tous les appareils connectés et génère des alertes si nécessaire'

    def handle(self, *args, **kwargs):
        self.stdout.write('Vérification des appareils en cours...')

        # Vérifier les bracelets connectés
        bracelets = ConnectedObject.objects.filter(type="bracelet")
        for bracelet in bracelets:
            check_bracelet_alerts(bracelet)

        # Vérifier les capteurs de qualité de l'air
        check_air_quality_sensors()

        # Vérifier les capteurs de porte
        check_door_sensors()

        self.stdout.write(self.style.SUCCESS('Vérification terminée !'))