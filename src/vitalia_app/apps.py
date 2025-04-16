from django.apps import AppConfig


class SiteConfig(AppConfig):
    name = 'Site'

class VitaliaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vitalia_app'

    def ready(self):
        import signals

