from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('admin', 'Responsable du site'),
    ('directeur', 'Directeur'),
    ('chef_inf', 'Chef des infirmiers'),
    ('infirmier', 'Infirmier'),
    ('aide_soignant', 'Aide-soignant'),
    ('menage', 'Ménage'),
    ('reception', 'Réceptionniste'),
    ('visiteur_site', 'Visiteur du site'),
    ('visiteur_resident', 'Visiteur des résidents'),
    ('retraite', 'Retraité'),
]

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    # A ajouter gestion des points et niveau

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
