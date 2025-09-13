from django.apps import AppConfig


class IntikhbAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    
    def ready(self):
        # Import signal handlers to ensure they are connected
        import app.signals
