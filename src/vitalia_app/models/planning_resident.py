from django.db import models
from django.contrib.auth.models import User

class PlanningEventResident(models.Model):
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.subject} ({self.resident.username})"
