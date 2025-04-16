from django.apps import AppConfig

class VitaliaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vitalia_app'

    def ready(self):
        import vitalia_app.signals

