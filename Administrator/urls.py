from django.urls import path
from Administrator import views

app_name = 'Administrator'

urlpatterns = [
    path('Dashboard/', views.AdminDashboard, name='admin_dashboard'),
    path('Semester/', views.Semester, name='semester'),
    path('DeleteSemester/<int:id>/', views.DeleteSemester, name='delete_semester'),
    path('Subject/', views.Subject, name='subject'),
    path('DeleteSubject/<int:id>/', views.DeleteSubject, name='delete_subject'),
    path('Teacher/', views.Teacher, name='teacher'),
    path('DeleteTeacher/<int:id>/', views.DeleteTeacher, name='delete_teacher'),
    path('AssignSubject/', views.AssignSubject, name='assign_subject'),
    path('DeleteAssignSubject/<int:id>/', views.DeleteAssignSubject, name='delete_assign_subject'),
    path('ViewComplaints/', views.ViewComplaints, name='view_complaints'),
    path('ViewUsers/', views.ViewUsers, name='view_users'),
    path('DeleteUser/<int:id>/', views.DeleteUser, name='delete_user'),
    path('GenerateTimeTable/', views.GenerateTimeTable, name='generate_timetable'),
]

