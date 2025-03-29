"""Сервис для работы с видеопотоком"""
import os
import signal
import subprocess
from dataclasses import dataclass
from typing import Union, Tuple

import psutil

from service import rtsp
from utils.secure import base64_hasher


@dataclass
class CameraEntity:
    """Сущность камеры"""
    id: int
    rtsp_link: str
    stream_app: str
    stream_name: str
    has_audio: bool
    stop: bool
    pause: bool
    detail_log: bool

    @property
    def stream_service(self) -> 'CameraStreamService':
        return CameraStreamService(self)

    @property
    def files_service(self) -> 'CameraFilesService':
        return CameraFilesService(self)

    @property
    def stream(self) -> str:
        """Формирование ссылки на rtmp поток"""
        return f'rtmp://nginx/{self.stream_app}/{self.stream_name}'

    @property
    def relative_playlist_path(self):
        return f'/hls/{self.stream_app}/{self.stream_name}/index.m3u8'

    def stream_url(self, domain_name: str) -> str:
        """Формирование ссылки на hls поток"""
        return f'{domain_name}{self.relative_playlist_path}'

    def get_playlist_link(self, domain_name: str, secure_key: Union[str, None]) -> str:
        """формирование ссылки на hls поток, с md5 хэшем"""
        hash_str = f'{self.relative_playlist_path} {secure_key}'
        return f'{self.stream_url(domain_name)}?md5={base64_hasher(hash_str)}'

    def hash_key(self, secure_key: str) -> str:
        """Формирование проверочного хэш ключа камеры"""
        hash_str = f'{self.stream_app}{self.stream_name} {secure_key}'
        return base64_hasher(hash_str)


class CameraStreamService:
    """класс, имплементирующий логику работы видео потоков"""
    def __init__(self, camera: CameraEntity):
        self.camera = camera

    def ffmpeg_cmd(self, log_dir: str):
        """
        Формирование строки с командой на запуск стрима из RTSP в RTMP
        """
        audio_flag = '' if self.camera.has_audio else '-f lavfi -i anullsrc'
        loglevel = 'level+verbose' if self.camera.detail_log else 'error'
        log_path = os.path.join(log_dir, 'logs/%s.log' % self.camera.stream_name)
        cmd_args = ('-avoid_negative_ts make_zero -fflags nobuffer -flags low_delay '
                    '-strict experimental -fflags +genpts+discardcorrupt '
                    '-use_wallclock_as_timestamps 1 -sc_threshold 0 -vcodec copy '
                    '-acodec aac -f flv')
        cmd = ('ffmpeg -hide_banner -loglevel %s %s -rtsp_transport '
               'tcp -i "%s" %s rtmp://nginx/%s/%s 2>%s &'
               % (loglevel, audio_flag, self.camera.rtsp_link, cmd_args, self.camera.stream_app,
                  self.camera.stream_name, log_path))
        return cmd

    def check_stream(self) -> Union[bool, list]:
        """Проверка запущен ли ffmpeg процесс для стрима"""
        try:
            pid_list = [proc.pid for proc in psutil.process_iter()
                        if self.camera.stream in proc.cmdline()]
        except psutil.NoSuchProcess:
            pid_list = False
        if not pid_list:
            pid_list = False
        return pid_list

    def start_ffmpeg_cmd(self, work_path: str, log: bool = False) -> Union[bool, str]:
        log_path = os.path.join(work_path, 'logs/%s.log' % self.camera.stream_name)
        check = rtsp.ffprobe_check_rtsp_error(self.camera.rtsp_link)
        if 'error' not in check:
            subprocess.call(self.ffmpeg_cmd(log_path), shell=True)
        else:
            if log:
                return check['error']['string']
        return True

    def start_stream(
            self, work_path: str, log=False
    ) -> Tuple[Union[int, bool], dict, Union[bool, str]]:
        """Запуск стрима"""
        pid = False
        fields = {}
        start_result = None
        if not self.check_stream():
            start_result = self.start_ffmpeg_cmd(log=log, work_path=work_path)
            pid = self.check_stream()
            if pid:
                if self.camera.stop:
                    fields['stop'] = False
                if self.camera.pause:
                    fields['pause'] = False
                pid = pid[0]
        return pid, fields, start_result

    def restart_stream(self, work_path: str) -> dict:
        """Перезапуск стрима"""
        pid_list = self.check_stream()
        update_fields = {}
        if pid_list:
            for pid in pid_list:
                try:
                    p = psutil.Process(pid)
                    p.send_signal(signal.SIGINT)
                except psutil.NoSuchProcess:
                    pass
            self.start_ffmpeg_cmd(work_path=work_path, log=False)
            if self.camera.stop:
                update_fields['stop'] = False
            if self.camera.pause:
                update_fields['pause'] = False
        return update_fields

    def stop_stream(
            self, stop: bool = False, only_stop: bool = False
    ) -> Tuple[Union[bool, list], dict]:
        """
        Остановка стрима. Если передан параметр stop - значит стрим на сегодня закончен.
        """
        pid_list = self.check_stream()
        update_fields = {}
        if pid_list:
            for pid in pid_list:
                try:
                    p = psutil.Process(pid)
                    p.send_signal(signal.SIGINT)
                except psutil.NoSuchProcess:
                    pass
            if not only_stop:
                if stop:
                    update_fields['stop'] = True
                else:
                    update_fields['pause'] = True
        return pid_list, update_fields


class CameraFilesService:
    """класс, имплементирующий логику работы с файловой системой"""
    def __init__(self, camera: CameraEntity):
        self.camera = camera

    def check_playlist_exist(self, work_path: str) -> bool:
        """Проверка наличия файла плейлиста"""
        playlist = f'{work_path}{self.camera.relative_playlist_path}'
        return os.path.exists(playlist)

    def clean_folder(self, stream_root: str) -> int:
        """Удаление файлов из директрории стрима"""
        stream_dir = f'{stream_root}/{self.camera.stream_app}/{self.camera.stream_name}'
        if os.path.isdir(stream_dir):
            files = os.listdir(stream_dir)
            for f in files:
                filepath = os.path.join(stream_dir, f)
                try:
                    os.remove(filepath)
                except OSError:
                    pass
        return 1

    def clear_hls(self, stream_root: str) -> None:
        """удаление старых ts файлов"""
        os.nice(19)
        fd = os.path.join(stream_root, self.camera.stream_app, self.camera.stream_name)
        # 1. получаем список файлов в плейлисте
        fn = os.path.join(fd, 'index.m3u8')
        if os.path.exists(fn):
            fp = open(fn)
            line = fp.readline()
            old_ts = []
            first_ts = None
            while line:
                if '.ts' in line.strip():
                    first_ts = line.strip()
                    break
                line = fp.readline()
            fp.close()
            if os.path.isdir(fd):
                files = os.listdir(fd)
                if files and first_ts:
                    first_ts = os.path.join(fd, first_ts)
                    for i in files:
                        try:
                            if '.ts' in i and os.path.getmtime(os.path.join(fd, i)) < \
                                    os.path.getmtime(first_ts):
                                old_ts.append(i)
                        except OSError:
                            pass
            if old_ts:
                for f in old_ts:
                    filepath = os.path.join(fd, f)
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass
