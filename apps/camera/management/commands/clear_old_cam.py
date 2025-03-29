import os
import shutil

from django.core.management.base import BaseCommand

from apps.camera.models import Camera
from django.conf import settings


class Command(BaseCommand):
    """Удаление каталогов с записями удалённых камер"""

    @staticmethod
    def _get_old_dir_list(cam_list: list, dir_name: str) -> list:
        dir_list = []
        cam_dir = os.listdir(dir_name)
        for cam in cam_dir:
            if len(dir_list) > 5:
                break
            if cam not in cam_list:
                dir_list.append(os.path.join(dir_name, cam))
        return dir_list

    def handle(self, *args, **options):
        os.nice(19)
        stream_dir = os.path.join(settings.STREAM_ROOT, 'stream')
        cam_list = list(Camera.objects.values_list('stream_name', flat=True))
        # todo: перенести функционал удаления каталогов в CameraFilesService
        dir_for_remove = self._get_old_dir_list(cam_list, stream_dir)
        for d in dir_for_remove:
            shutil.rmtree(d, ignore_errors=True)
