from django.apps import AppConfig


class BibliotecaConfig(AppConfig):
    name = 'biblioteca'

    def ready(self):
        import biblioteca.signals
