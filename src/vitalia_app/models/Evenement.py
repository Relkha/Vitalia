from django.db import models
from django.contrib.auth.models import User

class Evenement(models.Model):
    employe = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evenements_employe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evenements_createur')
    subject = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    def __str__(self):
        return self.subject
