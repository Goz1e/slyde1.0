from django.urls import path, include
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('get-room/', get_room, name='get_room'),
    path('create-room/', create_room, name='create_room'),
    path('anon-room/', anon_room, name='anon_room'),
    path('<str:room_id>/', room, name='room'),
    path('<str:room_id>/settings', room_settings, name='room_settings'),
    path('<str:room_id>/<str:username>/<str:action>', admin_actions, name='admin_actions'),
]