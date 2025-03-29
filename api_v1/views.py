import logging
import datetime

from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import Http404
from django.conf import settings

from apps.camera.models import Camera
from apps.camera.services import stop_stream, restart_stream
from service import rtsp
from utils.secure import base64_hasher
from api_v1.serializers import CameraSerializer, CameraDetailSerializer, CameraInfoSerializer, \
    StreamSerializer


logger = logging.getLogger('stream_log')


class CheckView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'success': True}, status=status.HTTP_200_OK)


class HashedAPIView(APIView):
    serializer_class = None
    camera = None

    @property
    def _encoded_hash(self):
        return self.camera.to_domain().hash_key(settings.CAM_SECURE_KEY) if self.camera else ''

    def _get_response(self):
        return Response(self.serializer_class(self.camera).data)

    def perform_action(self):
        self.camera = Camera.objects.filter(stream_name=self.kwargs['cam']).first()
        if self.camera:
            return self.camera
        else:
            raise Http404

    def get(self, request, *args, **kwargs):
        r_hash = request.query_params.get('hash', None)
        if not r_hash:
            return Response({'error': 'Не передан параметр hash'},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_action()
        if r_hash != self._encoded_hash:
            return Response({'error': 'Не верное значение параметра hash'},
                            status=status.HTTP_400_BAD_REQUEST)
        return self._get_response()


class CameraInfoView(HashedAPIView):
    """Информация по камере"""
    serializer_class = StreamSerializer


class CameraDetailView(HashedAPIView):
    """Детализация по камере"""
    serializer_class = CameraDetailSerializer


class CameraCheckView(HashedAPIView):
    """Проверка доступности камеры"""
    serializer_class = CameraInfoSerializer


class RTSPCheckView(HashedAPIView):
    """Проверка RTSP ссылки - вывод информации"""

    @property
    def _encoded_hash(self):
        return base64_hasher(f'stream {settings.CAM_SECURE_KEY}')

    def _get_response(self):
        rtsp_link = self.request.query_params.get('rtsp_link', None)
        if not rtsp_link:
            return Response({'error': 'Не передан параметр rtsp_link'},
                            status=status.HTTP_400_BAD_REQUEST)
        r_detail = self.request.query_params.get('detail', None)
        return Response(rtsp.check_rtsp(rtsp_link, detail=r_detail))

    def perform_action(self):
        pass


class CameraCreateView(generics.CreateAPIView):
    serializer_class = CameraSerializer

    def get_serializer_context(self):
        context = super(CameraCreateView, self).get_serializer_context()
        encoded_hash = base64_hasher(f'stream {settings.CAM_SECURE_KEY}')
        context.update({
            'hash': encoded_hash
        })
        return context

    def post(self, request, *args, **kwargs):
        if 'stream_name' in request.data and 'rtsp_link' in request.data:
            qs = Camera.objects.filter(stream_name=request.data['stream_name'],
                                       rtsp_link=request.data['rtsp_link'])
            if qs.exists():
                serializer = self.serializer_class(instance=qs.first())
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        camera_time = serializer.validated_data.get('cameratime', None)
        serializer.save()
        if camera_time:
            camera_time_model = serializer.instance.cameratime_set.model
            camera_time_model.objects.bulk_create(
                [camera_time_model(
                    start_time=i['start_time'],
                    end_time=i['end_time'],
                    camera=serializer.instance) for i in camera_time]
            )


class CameraUpdateView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = CameraSerializer

    def get_object(self):
        qs = self.serializer_class.Meta.model.objects.filter(
            stream_name=self.request.data['stream_name']
        )
        if qs.exists():
            return qs.first()
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        camera = self.get_object()
        rtsp_link = serializer.validated_data.get('rtsp_link', None)
        has_audio = serializer.validated_data.get('has_audio', False)
        need_restart = False
        serializer.save()
        camera_time = serializer.validated_data.get('cameratime', None)
        if camera_time:
            time_delete_list = []
            time_create_list = []
            camera_time_model = serializer.instance.cameratime_set.model
            cameratime_qs = serializer.instance.cameratime_set.all()
            for i in camera_time:
                if not cameratime_qs.filter(
                        start_time=i['start_time'], end_time=i['end_time']
                ).exists():
                    time_create_list.append(camera_time_model(camera=serializer.instance,
                                                              start_time=i['start_time'],
                                                              end_time=i['end_time']))
            for ct in cameratime_qs:
                need_to_delete = True
                for t in camera_time:
                    if ct.start_time == datetime.time.fromisoformat(t['start_time']) and \
                            ct.end_time == datetime.time.fromisoformat(t['end_time']):
                        need_to_delete = False
                if need_to_delete:
                    time_delete_list.append(ct.id)
            if time_create_list:
                camera_time_model.objects.bulk_create(time_create_list)
            if time_delete_list:
                camera_time_model.objects.filter(pk__in=time_delete_list).delete()
        else:
            camera.cameratime_set.all().delete()
        if rtsp_link and rtsp_link != camera.rtsp_link:
            need_restart = True
        if has_audio != camera.has_audio:
            need_restart = True
        if need_restart:
            restart_stream(Camera.objects.get(pk=camera.pk))

    def get_serializer_context(self):
        context = super(CameraUpdateView, self).get_serializer_context()
        context.update({
            'hash': self.get_object().to_domain().hash_key(settings.CAM_SECURE_KEY)
        })
        return context


class CameraDeleteView(mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = CameraSerializer

    def get_object(self):
        camera = self.serializer_class.Meta.model.objects.filter(
            stream_name=self.request.data['stream_name']
        ).first()
        if not camera:
            raise Http404
        return camera

    def post(self, request, *args, **kwargs):
        camera = self.get_object()
        if camera.to_domain().hash_key(settings.CAM_SECURE_KEY) != request.data.get('hash'):
            return Response({'error': 'Ошибка в контрольной сумме'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not all([camera.stop, camera.pause]):
            stop_stream(camera)
        camera.to_domain().files_service.clean_folder()
        return self.destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        self.serializer_class.Meta.model.objects.filter(stream_name=instance.stream_name).delete()
