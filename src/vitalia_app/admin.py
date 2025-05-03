from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from .models.Profil import Profil
from .models.Chambre import Chambre
from .models.Objets import ConnectedObject, PermissionType, ObjectPermission


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
    filter_horizontal = ('permissions',)  


class ObjectPermissionInline(admin.TabularInline):
    model = ObjectPermission
    extra = 0
    verbose_name = "Objet connecté autorisé"
    verbose_name_plural = "Objets accessibles"
    filter_horizontal = ("permissions",)
    fk_name = "group"


class CustomGroupAdmin(GroupAdmin):
    inlines = [ObjectPermissionInline]


admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)


@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('numero', 'statut', 'get_resident_display')
    list_filter = ('statut',)
    search_fields = ('numero', 'resident__username', 'resident__first_name', 'resident__last_name')

    def get_resident_display(self, obj):
        if obj.resident:
            if obj.resident.first_name or obj.resident.last_name:
                return f"{obj.resident.first_name} {obj.resident.last_name}".strip()
            else:
                return obj.resident.username
        return "-"

    get_resident_display.short_description = 'Résident'