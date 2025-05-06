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
            # Vérifie le groupe ET si l'utilisateur a un prénom ou nom
            if (groupe_retraite in instance.groups.all()) and (instance.first_name or instance.last_name):
                DossierMedical.objects.get_or_create(patient=instance)
        except Group.DoesNotExist:
            pass  # Groupe "Retraité" inexistant


@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profil'):
        Profil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profil(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()

