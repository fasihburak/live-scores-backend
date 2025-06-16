from django.apps import AppConfig


class ScoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scores'

    def ready(self):
        import scores.signals  # Ensure signals are registered