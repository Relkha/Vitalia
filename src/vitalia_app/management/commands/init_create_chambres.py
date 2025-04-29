from django.core.management.base import BaseCommand
from ...models.Chambre import Chambre

class Command(BaseCommand):
    help = "Crée 20 chambres numérotées automatiquement si elles n'existent pas déjà."

    def handle(self, *args, **kwargs):
        for i in range(1, 21):  # Création des chambres 1 à 20
            numero_str = str(i)
            chambre, created = Chambre.objects.get_or_create(numero=numero_str)
            if created:
                self.stdout.write(self.style.SUCCESS(f"🛏️ Chambre {numero_str} créée."))
            else:
                self.stdout.write(f"↪️ Chambre {numero_str} déjà existante.")
