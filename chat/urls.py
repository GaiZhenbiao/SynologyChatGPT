from django.urls import path

from . import views

urlpatterns = [
    path('', views.predict, name='index'),
    path('webhook', views.read_webhook, name='index'),
]
