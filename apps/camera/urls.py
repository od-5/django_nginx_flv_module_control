from django.conf.urls import url

from .views import check_status

app_name = 'camera'
urlpatterns = [
    url(r'^$', check_status, name='view'),
]
