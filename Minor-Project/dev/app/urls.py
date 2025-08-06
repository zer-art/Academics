from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start_camera, name='start_camera'),
    path('stop/', views.stop_camera, name='stop_camera'),
    path('word/', views.get_word, name='get_word'),
    path('reset/', views.reset_word, name='reset_word'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('suggestions/', views.get_suggestions, name='get_suggestions'),
]
