import os
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.camera.models import Camera
from service.camera import CameraFilesService

__author__ = 'alexy'


class Command(BaseCommand):
    """
    Удаление устаревших ts файлов.

    """
    def handle(self, *args, **options):
        for i in Camera.objects.all():
            CameraFilesService(i.to_domain()).clear_hls(settings.STREAM_ROOT)
