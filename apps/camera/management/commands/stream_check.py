import asyncio
import logging
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.camera.models import Camera
from apps.camera.services import check_cam_access_time, start_stream, restart_stream


logger = logging.getLogger('stream_log')


async def restart_stream_task(cam):
    # async task: restart hang stream
    restart_stream(cam)


async def check_stream_active(cam):
    # async task: old way stream check
    if cam.to_domain().stream_service.check_stream():
        restart_stream(cam)
    else:
        start_stream(cam)


async def check_access_time(cam, active_stream_list):
    # async task: new way stream check
    check_cam_access_time(cam, active_stream_list)


async def stream_check():
    tasks = []

    def check_stream_bw_video():
        for stream in stream_list:
            name = stream['name']
            bw_video = int(stream['bw_video'])
            time = int(stream['time'])
            if bw_video < 8192 and time > 20000:
                for cam in Camera.objects.filter(stream_name=name):
                    logger.info('create asyncio task restart_stream(cam ID %s)' % cam.id)
                    task = asyncio.create_task(restart_stream_task(cam))
                    tasks.append(task)

    def self_camera_start():
        for cam in Camera.objects.all().prefetch_related('cameratime_set'):
            logger.info('create asyncio task check_access_time(cam ID %s)' % cam.id)
            task = asyncio.create_task(check_access_time(cam, active_stream_list))
            tasks.append(task)
    site_name = settings.SITE_NAME
    # get streams from stat_json
    s = requests.get(f'http://{site_name}/stat_json')
    if s.status_code == 404:
        s = requests.get(f'https://{site_name}/stat_json', verify=False)
    stream_list = s.json()['http-flv']['servers'][0]['applications'][0]['live']['streams']

    # restart hang streams
    check_stream_bw_video()

    # stream check
    active_stream_list = [stream['name'] for stream in stream_list]
    self_camera_start()

    logger.info('await asyncio tasks[%s]' % len(tasks))
    await asyncio.gather(*tasks)
    logger.info('tasks done')


class Command(BaseCommand):
    """
    Проверка запущенных потоков
    """
    def handle(self, *args, **options):
        asyncio.run(stream_check())
