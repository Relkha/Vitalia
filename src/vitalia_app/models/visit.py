from django.db import models
from django.conf import settings

class Visit(models.Model):
    STATUS_CHOICES = [
        ('validated', 'Validée'),
        ('cancelled', 'Annulée'),
    ]

    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visits')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='validated')

    def __str__(self):
        return f"Visite de {self.resident} le {self.date} à {self.time}"
