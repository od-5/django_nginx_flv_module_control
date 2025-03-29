from celery import schedules
from celery.task import periodic_task
import datetime

from django.core.management import call_command


@periodic_task(run_every=schedules.crontab())
def stream_check_task():
    call_command('stream_check')


@periodic_task(run_every=datetime.timedelta(hours=1))
def clear_old_ts_task():
    call_command('clear_old_ts')

@periodic_task(run_every=datetime.timedelta(minutes=20))
def periodic_camera_restart_task():
    call_command('restart_periodic_cam')


@periodic_task(run_every=datetime.timedelta(days=2))
def clear_old_cam_task():
    call_command('clear_old_cam')
