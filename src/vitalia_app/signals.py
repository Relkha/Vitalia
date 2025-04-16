from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profil

@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profil'):
        Profil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profil(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()

