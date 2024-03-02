from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('index2', views.index, name='index2'),

    path('user_register', views.user_register, name='user_register'),
    path('user_login', views.user_login, name='user_login'),
    path('signout', views.signout, name='signout'),
    path('create_workspace', views.create_workspace, name='create_workspace'),
    path('edit_workspace/<int:pk>/', views.edit_workspace, name='edit_workspace'),
    path('join_workspace', views.join_workspace, name='join_workspace'),
    path('chat/<int:pk>/', views.chat, name='chat'),
    path('send_message', views.send_message, name='send_message'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('view_user/<int:pk>/', views.view_user, name='view_user'),
    path('exit/<int:pk>/', views.exit, name='exit'),
    path('delete_workspace/<int:pk>/', views.delete_workspace, name='delete_workspace'),




]