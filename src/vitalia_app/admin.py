from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
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

from django.contrib import admin
from .models.Objets import ConnectedObject, PermissionType, ObjectPermission

@admin.register(PermissionType)
class PermissionTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'label')
    search_fields = ('code', 'label')

@admin.register(ConnectedObject)
class ConnectedObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status', 'room')
    list_filter = ('type', 'status')
    search_fields = ('name', 'description', 'room')

@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ('connected_object', 'group')
    list_filter = ('group',)
    search_fields = ('connected_object__name', 'group__name')
    filter_horizontal = ('permissions',)  # Permet de sélectionner les permissions plus facilement

class ObjectPermissionInline(admin.TabularInline):
    model = ObjectPermission
    extra = 0
    verbose_name = "Objet connecté autorisé"
    verbose_name_plural = "Objets accessibles"
    filter_horizontal = ("permissions",)
    fk_name = "group"

class CustomGroupAdmin(GroupAdmin):
    inlines = [ObjectPermissionInline]

# Remplacer l'ancien Group admin par le nouveau
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)