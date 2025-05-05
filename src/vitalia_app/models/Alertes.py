from django.db import models
from django.contrib.auth.models import User
from .Profil import Profil
from .Objets import ConnectedObject


class Alert(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'Haute'),
        ('medium', 'Moyenne'),
        ('low', 'Basse'),
    ]

    TYPE_CHOICES = [
        ('medical', 'Médicale'),
        ('security', 'Sécurité'),
        ('environmental', 'Environnement'),
        ('device', 'Équipement'),
    ]

    STATUS_CHOICES = [
        ('new', 'Nouvelle'),
        ('in-progress', 'En cours'),
        ('resolved', 'Résolue'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    # Relations
    device = models.ForeignKey(ConnectedObject, null=True, blank=True, on_delete=models.SET_NULL)
    resident = models.ForeignKey(Profil, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.get_priority_display()} - {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alerte'
        verbose_name_plural = 'Alertes'


class AlertHistory(models.Model):
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('acknowledge', 'Prise en charge'),
        ('resolve', 'Résolution'),
        ('comment', 'Commentaire'),
    ]

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_action_display()} - {self.timestamp}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('medical', 'Médicale'),
        ('security', 'Sécurité'),
        ('environmental', 'Environnement'),
        ('device', 'Équipement'),
        ('system', 'Système'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    related_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'