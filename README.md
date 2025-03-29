# django_nginx_flv_module_control
Проект, реализующий API для добавления rtsp потоков в nginx flv module, автозапуск потоков и поддержание их работоспособности

для запуска celery выполнить команды:
celery -A cms worker -l info -s ../tmp/celery-schedule --pidfile= --logfile=../logs/celery.log
celery -A cms beat -l info -s ../tmp/celerybeat-schedule --pidfile= --logfile=../logs/celery_beat.log

конфигурация docker оставлена за кадром.
