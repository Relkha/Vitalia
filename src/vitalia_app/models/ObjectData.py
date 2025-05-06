from django.db import models
from .Objets import ConnectedObject


class ObjectData(models.Model):
    connected_object = models.OneToOneField(ConnectedObject, on_delete=models.CASCADE, related_name='data')

    numeric_value = models.FloatField(null=True, blank=True)  # Pour température, qualité de l'air, etc.
    text_value = models.CharField(max_length=100, null=True, blank=True)  # Pour états comme ouvert/fermé
    boolean_value = models.BooleanField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Données de {self.connected_object.name}"