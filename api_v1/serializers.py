import json
from typing import Union

from rest_framework import serializers

from django.conf import settings

from apps.camera.models import Camera
from service import rtsp


class StreamSerializer(serializers.ModelSerializer):
    online = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = (
            'url',
            'online',
            'archive',
        )

    def get_url(self, obj) -> Union[str, None]:
        link = None
        if obj.to_domain().file_service.check_playlist_exist(settings.WORK_PATH):
            link = obj.to_domain().stream_url(settings.SITE_NAME)
        return link

    def get_online(self, obj) -> bool:
        return bool(obj.to_domain().stream_service.check_stream())


class CameraSerializer(serializers.ModelSerializer):
    hash = serializers.CharField(allow_blank=False, write_only=True)
    cameratime = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Camera
        fields = (
            'rtsp_link',
            'stream_name',
            'hash',
            'has_audio',
            'source',
            'timezone',
            'start_time',
            'end_time',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
            'cameratime'
        )

    def validate(self, data):
        if data.pop('hash') != self.context.get('hash'):
            raise serializers.ValidationError('Ошибка в контрольной сумме')
        return data

    def validate_cameratime(self, value):
        return [i for i in value if 'start_time' in i and 'end_time' in i]


class CameraInfoSerializer(serializers.ModelSerializer):
    rtsp_available = serializers.SerializerMethodField()
    has_process = serializers.SerializerMethodField()
    has_playlist = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = (
            'rtsp_link',
            'stream_name',
            'rtsp_available',
            'has_process',
            'has_playlist',
        )

    def get_rtsp_available(self, obj):
        res = rtsp.ffprobe_check_rtsp_error(obj.rtsp_link)
        return res if 'error' in res else {}

    def get_has_process(self, obj) -> Union[bool, list]:
        return obj.to_domain().stream_service.check_stream()

    def get_has_playlist(self, obj) -> bool:
        return obj.to_domain().files_service.check_playlist_exist(settings.WORK_PATH)


class CameraDetailSerializer(serializers.ModelSerializer):
    check = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = (
            'rtsp_link',
            'stream_name',
            'check',
        )

    def get_check(self, obj) -> dict:
        check = rtsp.ffprobe_check_rtsp_error(obj.rtsp_link)
        if 'error' not in check:
            output = json.loads(rtsp.ffprobe_check_rtsp(obj.rtsp_link))
            if 'streams' in output:

                return {
                    'codec': output['streams'][0]['codec_name'],
                    'width': output['streams'][0]['coded_width'],
                    'height': output['streams'][0]['coded_height'],
                    'audio':  'audio' in [i['codec_type'] for i in output['streams']]
                }
            else:
                return {
                    'codec': 'no codec inform'
                }
        else:
            return {}
