import os
import shutil
from time import sleep

from django.conf import settings
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import Camera
from .services import stop_stream


@receiver(pre_save, sender=Camera)
def cam_pre_save_signal(sender, instance, **kwargs):
    if instance.id:
        old_instance = sender.objects.get(pk=instance.id)
        if old_instance.rtsp_link != instance.rtsp_link or \
                old_instance.has_audio != instance.has_audio:
            stop_stream(instance, only_stop=True)


@receiver(pre_delete, sender=Camera)
def cam_pre_delete_signal(sender, instance, **kwargs):
    stop_stream(instance)
    sleep(2)
    hls_path = os.path.join(settings.STREAM_ROOT, instance.stream_app, instance.stream_name)
    if os.path.exists(hls_path):
        shutil.rmtree(hls_path)
