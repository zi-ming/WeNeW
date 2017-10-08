
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^(?P<id>\d+)', views.content, name="content"),
    url(r'^\D*$', views.news, name='news'),
]
