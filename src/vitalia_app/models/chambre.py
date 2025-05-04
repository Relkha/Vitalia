from django.db import models
from django.contrib.auth.models import User


class Chambre(models.Model):
    STATUT_CHOICES = [
        ('LIBRE', 'Libre'),
        ('RESERVE', 'Réservée'),
        ('OCCUPE', 'Occupée'),
    ]

    numero = models.CharField(max_length=10, unique=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='LIBRE')
    resident = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Chambre {self.numero} ({self.get_statut_display()})"