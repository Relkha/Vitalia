from django.db import models
from django.contrib.auth.models import User

NIVEAU_CHOICES = [
    ('debutant', 'Débutant'),
    ('intermediaire', 'Intermédiaire'),
    ('avance', 'Avancé'),
    ('expert', 'Expert'),
]
def upload_to(instance, filename):
    # Exemple : photos_residents/5_photo.png
    return f'photos_residents/{instance.user.id}_{filename}'

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.FloatField(default=0)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='debutant')
    photo = models.ImageField(upload_to=upload_to, blank=True, null=True)  # <-- Nouveau champ !

    def __str__(self):
        return f"{self.user.username} - {self.niveau}"

    def get_role(self):
        return self.user.groups.first().name if self.user.groups.exists() else "Aucun"

    def update_niveau(self):
        if self.points >= 7:
            self.niveau = 'expert'
        elif self.points >= 5:
            self.niveau = 'avance'
        elif self.points >= 3:
            self.niveau = 'intermediaire'
        else:
            self.niveau = 'debutant'
        self.save()
