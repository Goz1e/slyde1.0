from django.urls import path, include
from .views import *
urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('signup/', signup, name='signup'),
    path('settings/', settings, name='settings'),
    path('logout/', logout_view, name='logout'),
 ]