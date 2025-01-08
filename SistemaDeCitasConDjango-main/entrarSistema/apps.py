from django.apps import AppConfig

class EntrarSistemaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entrarSistema'

    def ready(self):
        import entrarSistema.signals  # Importa las señales

    

