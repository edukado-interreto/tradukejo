from django.apps import AppConfig


class TradukoConfig(AppConfig):
    name = "traduko"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import traduko.signals
