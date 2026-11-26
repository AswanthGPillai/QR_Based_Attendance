from django.urls import path
from Teacher import views

app_name = 'Teacher'

urlpatterns = [
    path('Dashboard/', views.TeacherDashboard, name='teacher_dashboard'),
    path('MyProfile/', views.MyProfile, name='my_profile'),
    path('EditProfile/', views.EditProfile, name='edit_profile'),
    path('ChangePassword/', views.ChangePassword, name='change_password'),
    path('ViewTimetable/', views.ViewTimetable, name='view_timetable'),
    path('SelectPeriodForQR/', views.SelectPeriodForQR, name='select_period_for_qr'),
    path('GenerateQRCode/<int:assign_id>/', views.GenerateQRCode, name='generate_qr_code'),
    path('GetDynamicToken/<int:session_id>/', views.GetDynamicToken, name='get_dynamic_token'),
    path('RenderQRImage/<str:token>/', views.RenderQRImage, name='render_qr_image'),
    path('CloseQRSession/<int:session_id>/', views.CloseQRSession, name='close_qr_session'),
    path('ViewAttendance/', views.ViewAttendance, name='view_attendance'),
]

