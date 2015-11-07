__author__ = 'prism'
__date__ = '30 May, 2015'

from django.conf.urls import include, url
from .views import Login, Logout


urlpatterns = [
    url(r'^$', Login.as_view(), name='auth'),
    url(r'^logout/$', Logout.as_view()),
]
