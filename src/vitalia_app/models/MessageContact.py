from django.db import models

class MessageContact(models.Model):
    OBJETS = [
        ('info', 'Demande d’informations'),
        ('visite', 'Demande de visite'),
        ('admission', 'Demande d’admission'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100)
    email = models.EmailField()
    objet = models.CharField(max_length=20, choices=OBJETS)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.objet}"


