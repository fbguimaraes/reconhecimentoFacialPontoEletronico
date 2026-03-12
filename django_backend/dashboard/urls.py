"""
URLs do Dashboard.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('employees/', views.employees_list, name='employees'),
    path('employees/<int:pk>/', views.employee_detail, name='employee-detail'),
    path('logs/', views.logs_list, name='logs'),
    path('reports/', views.reports, name='reports'),
]
