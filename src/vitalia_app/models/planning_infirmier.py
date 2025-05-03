
from django.db import models
from django.contrib.auth.models import User

class PlanningEventInfirmier(models.Model):
    subject = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    employe = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='planning_events')

    class Meta:
        verbose_name = "Événement de planning infirmier"
        verbose_name_plural = "Événements de planning infirmier"

    def __str__(self):
        return f"{self.subject} ({self.start_time} - {self.end_time})"

    def save(self, *args, **kwargs):
        # Assurez-vous que subject et title sont synchronisés
        if not self.title and self.subject:
            self.title = self.subject
        elif not self.subject and self.title:
            self.subject = self.title
        super().save(*args, **kwargs)