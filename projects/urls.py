from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/register/', views.u_register, name='register'),
    path('dashboard/', views.project_dashboard, name='project_dashboard'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('login/', views.u_login, name='login'),
    path('about/', views.about, name='about'),
]