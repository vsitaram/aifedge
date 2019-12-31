from django.urls import path

from . import views

app_name = 'edge'
urlpatterns = [
	path('', views.dashboard, name='dashboard'),
    path('pitches/', views.pitches, name='pitches'),
    path('pitches/<int:pitch_id>/', views.pitch, name='pitch')
]