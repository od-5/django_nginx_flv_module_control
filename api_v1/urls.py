from rest_framework.urlpatterns import format_suffix_patterns

from django.conf.urls import url

from api_v1 import views

app_name = 'api_v1'
urlpatterns = (
    url(r'^$', views.CheckView.as_view(), name='check'),
    url(r'^check/available/(?P<cam>[\w-]+)/$', views.CameraCheckView.as_view(), name='check'),
    url(r'^check/full/(?P<cam>[\w-]+)/$', views.CameraDetailView.as_view(), name='detail'),
    url(r'^rtsp_check/$', views.RTSPCheckView.as_view(), name='rtsp-check'),
    url(r'^add/$', views.CameraCreateView.as_view(), name='add'),
    url(r'^info/(?P<cam>[\w-]+)/$', views.CameraInfoView.as_view(), name='info'),
    url(r'^update/$', views.CameraUpdateView.as_view(), name='update'),
    url(r'^delete/$', views.CameraDeleteView.as_view(), name='delete'),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
