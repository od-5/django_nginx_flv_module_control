"""функции вызовы ffprobe"""
import json
import subprocess


def ffprobe_check_rtsp(rtsp_link: str) -> bytes:
    """вызов ffprobe"""
    cmds = ['ffprobe', '-rtsp_transport', 'tcp', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', rtsp_link]
    curl_p = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output, _ = curl_p.communicate()
    return output


def ffprobe_check_rtsp_error(rtsp_link: str) -> dict:
    """Проверка наличия ошибок в RTSP потоке через ffprobe"""
    cmds = ['ffprobe', '-rtsp_transport', 'tcp', '-timeout', '2000000', '-v', 'quiet',
            '-print_format', 'json', '-show_error', rtsp_link]
    proc = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, _ = proc.communicate()
    try:
        response = json.loads(output)
    except Exception as e:
        print('ffprobe_check_rtsp_error => ', str(e))
        response = {}
    if 'error' in response and 'string' in response['error']:
        if response['error']['string'] == 'End of file':
            response.pop('error')
        elif response['error']['string'] == 'Connection timed out':
            response['error']['string'] = 'Превышено время ожидания ответа от камеры. ' \
                                          'Возможные причин: проблемы с пробросом портов, ' \
                                          'каналом связи, доступностью устройства'
        elif response['error']['string'] == 'Operation not permitted':
            response['error']['string'] = 'Операция не разрешена. Проверьте настройки прав ' \
                                          'доступа на оборудовании'
        elif response['error']['string'] == 'Invalid data found when processing input':
            response['error']['string'] = 'Ошибка в обработке ответа от камеры. Проверьте ' \
                                          'работоспособность камеры или регистратора'
        elif response['error']['string'] == 'Server returned 4XX Client Error, but not one ' \
                                            'of 40{0,1,3,4}':
            response['error']['string'] = 'Устройство ответило сообщением об ошибке. ' \
                                          'Проверьте работоспособность камеры или регистратора'
        elif response['error']['string'] == 'Connection refused':
            response['error']['string'] = 'Соединение с устройством сброшено. Проверьте ' \
                                          'настройки проброса портов и доступность оборудования'
    return response


def check_rtsp(rtsp_link: str, detail=True) -> dict:
    """проверка доступности rtsp ссылки и наличия видеопотока"""
    check = ffprobe_check_rtsp_error(rtsp_link)
    resp = {'available': False}
    if check and 'error' not in check:
        if detail:
            output = ffprobe_check_rtsp(rtsp_link)
            output = json.loads(output)
            if 'streams' in output:
                resp['available'] = True
                resp['streams'] = output
            else:
                resp['available'] = True
                resp['streams'] = None
        else:
            resp['available'] = True
    return resp
