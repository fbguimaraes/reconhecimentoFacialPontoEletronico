"""
URL patterns para a API de funcionários e reconhecimento facial.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'logs', views.TimeLogViewSet, basename='timelog')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints de reconhecimento facial
    path('recognize/', views.recognize_face, name='recognize-face'),
    path('recognize-image/', views.recognize_image, name='recognize-image'),
    path('register-employee-image/', views.register_employee_image, name='register-employee-image'),
    path('register-employee/', views.register_employee, name='register-employee'),
    path('register-log/', views.register_log, name='register-log'),
    path('check-duplicate/', views.check_duplicate_face, name='check-duplicate'),
    
    # Dashboard stats
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
