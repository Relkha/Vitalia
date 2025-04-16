from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.apps import apps


GROUPS_PERMISSIONS = {
    "Responsable du site": "__all__",
    "Directeur": [
        "view_user", "change_user",
        "add_profil", "change_profil", "view_profil",
    ],
    "Chef des infirmiers": [
        "change_profil", "view_profil",
    ],
    "Infirmier": [
        "view_profil",
    ],
    "Aide-soignant": [],
    "Ménage": [],
    "Réceptionniste": [
        "view_user",
    ],
    "Visiteur du site": [],
    "Visiteur des résidents": [],
    "Retraité": [],
}

def create_groups():
    for group_name, perms in GROUPS_PERMISSIONS.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"✅ Groupe '{group_name}' créé.")
        else:
            print(f"↪️ Groupe '{group_name}' déjà existant.")

        if perms == "__all__":
            group.permissions.set(Permission.objects.all())
            print(f"🔐 Toutes les permissions attribuées à '{group_name}'.")
        else:
            permission_objs = []
            for codename in perms:
                try:
                    perm = Permission.objects.get(codename=codename)
                    permission_objs.append(perm)
                except Permission.DoesNotExist:
                    print(f"❌ Permission non trouvée : {codename}")
            group.permissions.set(permission_objs)
            print(f"🔐 {len(permission_objs)} permission(s) attribuées à '{group_name}'.")

create_groups()
