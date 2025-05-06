from django.db import models

class Room(models.Model):
    numero = models.IntegerField()

    def __str__(self):
        return f"Salle {self.numero}"
