from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

from . import views

app_name = 'edge'
urlpatterns = [
	path('', views.dashboard, name='dashboard'),
    path('pitches/', views.pitches, name='pitches'),
    path('pitches/<int:pitch_id>/', views.pitch, name='pitch'),

    path('login/', auth_views.LoginView.as_view(template_name="edge/login_new.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]