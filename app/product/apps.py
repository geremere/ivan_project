from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'app.product'

    def ready(self):
        from jobs import update
        update.start()
