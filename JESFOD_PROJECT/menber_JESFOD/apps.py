from django.apps import AppConfig


class MenberJesfodConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'menber_JESFOD'

    def ready(self):
        import menber_JESFOD.signals

