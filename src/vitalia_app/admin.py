from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.Profil import Profil


class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = "Profil"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_niveau')
    list_select_related = ('profil',)

    def get_role(self, instance):
        return instance.profil.get_role() if hasattr(instance, 'profil') else "Aucun"

    def get_niveau(self, instance):
        return instance.profil.niveau if hasattr(instance, 'profil') else "-"

    get_role.short_description = 'Rôle'
    get_niveau.short_description = 'Niveau'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
