from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from . import views

app_name = 'edge'
urlpatterns = [
	path('', views.dashboard, name='dashboard'),
	path('dashboard/<str:time_horizon>', views.dashboard_graph_data, name='dashboard_graph_data'),
    path('pitches/', views.pitches, name='pitches'),
    path('pitches/<int:pitch_id>/', views.pitch, name='pitch'),
    path('tools/', views.tools, name='tools'),
    path('tools/<int:tool_id>/', views.tool, name='tool'),

    path('login/', auth_views.LoginView.as_view(template_name="edge/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]