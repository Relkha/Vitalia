from django.contrib import admin
from .models.Profil import Profil

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
