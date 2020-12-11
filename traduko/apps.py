from django.apps import AppConfig


class TradukoConfig(AppConfig):
    name = 'traduko'

    def ready(self):
        import traduko.signals
