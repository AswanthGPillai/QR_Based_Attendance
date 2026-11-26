from django.urls import path
from Student import views

app_name = 'Student'

urlpatterns = [
    path('Dashboard/', views.StudentDashboard, name='student_dashboard'),
    path('MyProfile/', views.MyProfile, name='my_profile'),
    path('EditProfile/', views.EditProfile, name='edit_profile'),
    path('ChangePassword/', views.ChangePassword, name='change_password'),
    path('ViewTimetable/', views.ViewTimetable, name='view_timetable'),
    path('ScanQR/', views.ScanQR, name='scan_qr'),
    path('ViewAttendance/', views.ViewAttendance, name='view_attendance'),
    path('Complaints/', views.Complaints, name='complaints'),
]

