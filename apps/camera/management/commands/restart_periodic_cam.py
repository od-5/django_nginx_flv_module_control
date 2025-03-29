import asyncio

from django.core.management.base import BaseCommand

from apps.camera.models import Camera
from apps.camera.services import restart_stream as service_restart_stream


async def restart_stream(cam):
    # async task: restart hang stream
    service_restart_stream(cam)


async def command_call():
    tasks = []
    for cam in Camera.objects.filter(periodic_restart=True):
        task = asyncio.create_task(restart_stream(cam))
        tasks.append(task)
    await asyncio.gather(*tasks)


class Command(BaseCommand):
    """
    Перезапуск камер с periodic_restart=True
    """
    def handle(self, *args, **options):
        asyncio.run(command_call())
