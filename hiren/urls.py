"""hiren URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from django.conf import settings
from mail.views import AccountViewSet
from mail import views

if settings.DEBUG:
    router = routers.DefaultRouter()
else:
    router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)


if settings.DEBUG:
    urlpatterns = [
        url(r'^create_admin/', views.create_admin),
        url(r'^user_list/', views.GetUserList.as_view()),
        url(r'^api-token-auth/', obtain_jwt_token),
        url(r'^api/', include(router.urls)),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^docs/', include('rest_framework_swagger.urls')),
        url(r'^', TemplateView.as_view(template_name='index.html')),
    ]
else:
    urlpatterns = [
        url(r'^api/', include(router.urls)),
        url(r'^api-token-auth/', obtain_jwt_token),
        url(r'^', TemplateView.as_view(template_name='index.html')),
    ]
