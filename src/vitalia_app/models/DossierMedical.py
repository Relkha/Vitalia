from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DossierMedical(models.Model):
    patient = models.OneToOneField(User, on_delete=models.CASCADE)
    infirmier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultations_faites')
    consultation = models.TextField(blank=True, null=True)
    etat = models.CharField(max_length=255, blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    date_entree = models.DateField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_view_dossier", "Peut voir le dossier"),
            ("can_edit_own_consultation", "Peut modifier sa propre consultation"),
        ]

    def __str__(self):
        return f"Dossier de {self.patient.get_full_name()}"
