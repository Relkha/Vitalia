from django.db import models
from django.contrib.auth.models import User

class PlanningEventInfirmier(models.Model):
    subject = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    employe = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"

