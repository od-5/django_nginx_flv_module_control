from django.contrib import admin
from django.conf import settings

from apps.camera.models import Camera


class CameraAdmin(admin.ModelAdmin):
    list_display = ('rtsp_link', 'stream_name', 'has_audio', 'playlist', 'stop', 'detail_log',
                    'periodic_restart')

    @admin.display()
    def playlist(self, obj):
        return obj.to_domain().get_playlist_link(settings.SITE_NAME, settings.CAM_SECURE_KEY)


admin.site.register(Camera, CameraAdmin)
