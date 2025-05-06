from django.db import models
from django.contrib.auth.models import Group
from .Chambre import Chambre

class PermissionType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=120)

    def __str__(self):
        return self.label

class ConnectedObject(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    room = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name='objets_connectes')  # 🔥
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Actif'), ('inactive', 'Inactif')],
        default='active'
    )

    value = models.CharField(max_length=50, blank=True, null=True)  # 💡 Peut contenir 22.3, moyenne, etc.


    def __str__(self):
        return self.name

class ObjectPermission(models.Model):
    connected_object = models.ForeignKey(ConnectedObject, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(PermissionType)

    class Meta:
        unique_together = ('connected_object', 'group')

    def __str__(self):
        return f"{self.group.name} - {self.connected_object.name}"
