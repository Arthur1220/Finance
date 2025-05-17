from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # importa o módulo que registra o plugin no plugin_dir
        import core.healthchecks  
