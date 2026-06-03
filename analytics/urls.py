from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_csv_view, name='upload_csv'),
    path('users/', views.manage_users_view, name='manage_users'),
    path('users/<int:user_id>/edit/', views.edit_user_view, name='edit_user'),
    path('courses/', views.courses_view, name='courses_list'),
    path('courses/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('students/', views.students_view, name='students_list'),
    path('students/<int:student_id>/', views.student_detail_view, name='student_detail'),
    path('alerts/', views.risk_alerts_view, name='risk_alerts'),
    path('reports/pdf/', views.export_pdf_report, name='export_pdf'),
    path('reports/excel/', views.export_excel_report, name='export_excel'),
]
