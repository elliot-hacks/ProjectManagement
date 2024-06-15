from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/register/', views.u_register, name='register'),
    path('dashboard/', views.project_dashboard, name='project_dashboard'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('division/<int:division_id>/', views.division_detail, name='division_detail'),
    path('ward/<int:ward_id>/', views.ward_detail, name='ward_detail'),
    path('village/<int:village_id>/', views.village_detail, name='village_detail'),
    path('task/<int:project_id>/', views.create_task, name='create_task'),
    path('project_report', views.project_report, name='project_report'),
    path('login/', views.u_login, name='login'),
    path('about/', views.about, name='about'),
    path('project/', views.project, name='project'),
    path('service/', views.service, name='service'),
]