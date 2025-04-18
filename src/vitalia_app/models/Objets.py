from django.db import models
from django.contrib.auth.models import Group

class PermissionType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=120)

    def __str__(self):
        return self.label

class ConnectedObject(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    room = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Actif'), ('inactive', 'Inactif')], default='active')

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
