from django.urls import path, re_path, include
from django.contrib.auth.views import logout
from base import views

urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('settings/', views.settings, name='settings'),
    path('domain/<int:pk>/delete/', views.delete_domain, name='delete_domain'),
    path('domain/<int:pk>/', views.update_domain, name='update_domain'),
    path('domain/', views.create_domain, name='create_domain'),
    path('user/<str:username>/', views.update_user, name='update_user'),
    path('user/', views.create_user, name='create_user'),
    path('logout/', logout, {'next_page': '/'}, name='logout'),
]
