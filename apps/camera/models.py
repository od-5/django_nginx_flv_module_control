from django.db import models

from service.camera import CameraEntity


class CameraTimeBase(models.Model):
    start_time = models.TimeField(verbose_name='Время начала', blank=True, null=True)
    end_time = models.TimeField(verbose_name='Время окончания', blank=True, null=True)

    class Meta:
        abstract = True


class Camera(CameraTimeBase):
    TIME_CHOICES = tuple((i, i) for i in range(-12, 13))

    rtsp_link = models.CharField(verbose_name='RTSP поток', max_length=256)
    stream_app = models.CharField(verbose_name='Приложение', max_length=10, default='stream')
    stream_name = models.CharField(verbose_name='Поток', max_length=20, default='cam')
    pid = models.IntegerField(verbose_name='PID процесса', blank=True, null=True)
    stop = models.BooleanField(verbose_name='Трансляция закончена', default=False)
    pause = models.BooleanField(verbose_name='Трансляция приостановлена', default=False)
    has_audio = models.BooleanField(verbose_name='Камера со звуком', default=False)
    detail_log = models.BooleanField(verbose_name='Включить детальный лог ', default=False)
    source = models.CharField(verbose_name='источник добавления', max_length=256, blank=True,
                              null=True)
    timezone = models.SmallIntegerField(verbose_name=u'Часовой пояс', default=3,
                                        choices=TIME_CHOICES)
    monday = models.BooleanField(verbose_name='Понедельник', default=True)
    tuesday = models.BooleanField(verbose_name='Вторник', default=True)
    wednesday = models.BooleanField(verbose_name='Среда', default=True)
    thursday = models.BooleanField(verbose_name='Четверг', default=True)
    friday = models.BooleanField(verbose_name='Пятница', default=True)
    saturday = models.BooleanField(verbose_name='Суббота', default=True)
    sunday = models.BooleanField(verbose_name='Воскресенье', default=True)
    periodic_restart = models.BooleanField(verbose_name='Перезапускать каждые 20 минут',
                                           default=False)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Камера'
        verbose_name_plural = 'Камеры'

    def __str__(self):
        return f'{self.stream_app}/{self.stream_name}'

    def to_domain(self) -> CameraEntity:
        return CameraEntity(
            id=self.id, rtsp_link=self.rtsp_link, stream_app=self.stream_app,
            stream_name=self.stream_name, has_audio=self.has_audio, detail_log=self.detail_log,
            stop=self.stop, pause=self.pause
        )

    def get_allow_days(self):
        """
        Список дней доступных для вещания видеопотока
        """
        days = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
        allow_days_index = []
        i = 0
        for day in days:
            if getattr(self, day):
                allow_days_index.append(i)
            i += 1
        return allow_days_index


class CameraTime(CameraTimeBase):
    camera = models.ForeignKey(to=Camera, verbose_name='Камера', on_delete=models.CASCADE)

    class Meta:
        ordering = ['start_time']
        verbose_name = 'Настройка камеры'
        verbose_name_plural = 'Настройки камеры'

    def __str__(self):
        return 'Перерыв в работе камеры'
