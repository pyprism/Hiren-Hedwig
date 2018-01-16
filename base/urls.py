from django.urls import path, re_path, include
from django.contrib.auth.views import logout
from base import views

urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('settings/', views.settings, name='settings'),
    path('domain/<int:pk>/', views.update_domain, name='update_domain'),
    path('domain/', views.create_domain, name='create_domain'),
    path('logout/', logout, {'next_page': '/'}, name='logout'),
]