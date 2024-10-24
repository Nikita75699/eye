from django.urls import path
from . import views
from django.contrib.auth import views
from .views import migrate_data

urlpatterns = [
    path('migrate', migrate_data, name='migrate_data'),
]