from django.urls import path, re_path
from mail import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('thread/<int:pk>/', views.inbox_details, name='thread'),
    path('thread/delete/<int:thread_id>/<int:mail_id>/', views.thread_delete, name='thread_delete'),
    path('thread/reply/<int:thread_id>/<int:mail_id>/', views.thread_reply, name='thread_reply'),
    path('compose/', views.compose, name='compose'),
    path('sent/', views.sent, name='sent'),
    path('draft/', views.draft, name='draft'),
    path('queue/', views.queue, name='queue'),
    path('trash/', views.trash, name='trash'),
    path('trash/<int:pk>/delete/', views.trash_delete, name='trash_delete'),
    path('sent/<int:pk>/delete/', views.sent_delete, name='sent_delete'),
    path('<int:pk>/', views.mail_by_id, name='mail_by_id'),
    path('draft/<int:pk>/edit/', views.draft_edit, name='draft_edit'),
]
