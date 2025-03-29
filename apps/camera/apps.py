from django.apps import AppConfig


class CameraAppConfig(AppConfig):
    name = 'apps.camera'

    def ready(self):
        import apps.camera.signals  # noqa