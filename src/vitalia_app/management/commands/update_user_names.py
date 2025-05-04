from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Met à jour les first_name et last_name des utilisateurs si vides'

    def handle(self, *args, **options):
        users_updated = 0

        for user in User.objects.all():
            if not user.first_name and not user.last_name:
                # Exemple : si le username est "jean.dupont", on peut extraire le nom
                if '.' in user.username:
                    parts = user.username.split('.')
                    user.first_name = parts[0].capitalize()
                    user.last_name = parts[1].capitalize()
                else:
                    # Si le username ne contient pas de point, on met juste le username comme nom
                    user.first_name = user.username
                    user.last_name = ""

                user.save()
                users_updated += 1
                self.stdout.write(f"Mis à jour: {user.username}")

        self.stdout.write(self.style.SUCCESS(f'Terminé. {users_updated} utilisateurs mis à jour.'))