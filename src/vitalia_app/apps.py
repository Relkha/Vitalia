from django.apps import AppConfig

class VitaliaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vitalia_app'

    def ready(self):
        #from .initial_setup import create_default_groups
        #create_default_groups()
        pass



