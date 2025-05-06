from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profil

#AJout
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import DossierMedical

User = get_user_model()

@receiver(post_save, sender=User)
def create_dossier_for_retiree(sender, instance, created, **kwargs):
    if created:
        try:
            groupe_retraite = Group.objects.get(name="Retraité")
            if groupe_retraite in instance.groups.all():
                DossierMedical.objects.get_or_create(patient=instance)
        except Group.DoesNotExist:
            # Si le groupe "retraité" n'existe pas encore
            pass


@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profil'):
        Profil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profil(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def ajouter_points_connexion(sender, user, request, **kwargs):
    if hasattr(user, "profil"):
        user.profil.points += 0.25
        user.profil.update_niveau()

