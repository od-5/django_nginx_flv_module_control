import datetime
from typing import Union

from django.conf import settings

from apps.camera.models import Camera


def check_cam_access_time(camera, active_stream_list=None):
    if not active_stream_list:
        active_stream_list = []
    stream_service = camera.to_domain().stream_service
    c_date = datetime.datetime.now() + datetime.timedelta(hours=camera.timezone)
    c_time = c_date.time()
    delta_start_time = (c_date + datetime.timedelta(seconds=30)).time()
    weekday = c_date.weekday()
    if camera.start_time and camera.end_time:
        # проеряем рабочий день камеры
        if weekday in camera.get_allow_days():
            # проверяем время начала и окончания работы
            if camera.start_time <= delta_start_time and c_time < camera.end_time:
                # проверяем перерывы по камере
                if camera.cameratime_set.filter(
                        start_time__lte=c_time, end_time__gte=delta_start_time
                ).exists():
                    stop_stream(camera, stop=False)
                else:
                    if camera.stream_name not in active_stream_list:
                        if stream_service.check_stream():
                            print(f'services.py:22 - camera {camera.stream_name} '
                                  f'RESTART, because not in '
                                  f'active_stream_list={active_stream_list}')
                            restart_stream(camera)
                        else:
                            print(f'services.py:26 - camera {camera.stream_name} '
                                  f'START, because not in '
                                  f'active_stream_list={active_stream_list}')
                            start_stream(camera, log=True)
            else:
                # трансляция должна быть остановлена, т.к. нерабочее время
                stop_stream(camera, stop=True)
        else:
            # трансляция должна быть остановлена, т.к. нерабочий день
            stop_stream(camera, stop=True)
    else:
        if camera.stream_name not in active_stream_list:
            if stream_service.check_stream():
                restart_stream(camera)
            else:
                start_stream(camera, log=True)
    return True


def _update_fields(camera: Camera, fields: dict) -> None:
    """вспомогательная функция обновления данных в объекте"""
    if fields:
        if fields:
            for field in fields:
                setattr(camera, field, fields[field])
            camera.save(update_fields=[fields.keys()])


def start_stream(
        camera: Camera, log: bool = False
) -> Union[int, bool]:
    """запуск трансляции"""
    pid, fields, result = camera.to_domain().stream_service.start_stream(settings.WORK_PATH, log)
    _update_fields(camera, fields)
    return pid


def stop_stream(
        camera: Camera, stop: bool = False, only_stop: bool = False
) -> Union[bool, list]:
    """остановка трансляции"""
    pid_list, fields = camera.to_domain().stream_service.stop_stream(stop=stop,
                                                                     only_stop=only_stop)
    _update_fields(camera, fields)
    return pid_list


def restart_stream(camera: Camera) -> None:
    """перезапуск трансляции"""
    fields = camera.to_domain().stream_service.restart_stream(settings.WORK_PATH)
    _update_fields(camera, fields)
