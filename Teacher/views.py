from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from Administrator.models import (
    tbl_teacher, tbl_assign_subject, tbl_timetable,
    tbl_qrsession, tbl_attendance, tbl_student
)
import datetime
import uuid
import qrcode
import io

# ==============================================================================
# Helper to check Teacher session
# ==============================================================================
def check_teacher_session(request):
    return 'tid' in request.session

# ==============================================================================
# TEACHER DASHBOARD
# ==============================================================================
def TeacherDashboard(request):
    if not check_teacher_session(request):
        return redirect('Guest:login')

    teacher = tbl_teacher.objects.get(id=request.session['tid'])
    assigned_count = tbl_assign_subject.objects.filter(teacher=teacher).count()
    today_name = datetime.date.today().strftime('%A')
    today_classes = tbl_timetable.objects.filter(assign_subject__teacher=teacher, day=today_name).order_by('period')

    context = {
        'teacher': teacher,
        'assigned_count': assigned_count,
        'today_name': today_name,
        'today_classes': today_classes,
    }
    return render(request, 'Teacher/TeacherDashboard.html', context)

# ==============================================================================
# 1. MY PROFILE
# ==============================================================================
def MyProfile(request):
    if not check_teacher_session(request):
        return redirect('Guest:login')

    teacher = tbl_teacher.objects.get(id=request.session['tid'])
    return render(request, 'Teacher/MyProfile.html', {'teacher': teacher})

# ==============================================================================
# 2. EDIT PROFILE
# ==============================================================================
def EditProfile(request):
    if not check_teacher_session(request):
        return redirect('Guest:login')

    teacher = tbl_teacher.objects.get(id=request.session['tid'])

    if request.method == "POST":
        teacher.teacher_name = request.POST.get('txt_name')
        teacher.teacher_contact = request.POST.get('txt_contact')
        teacher.teacher_qualification = request.POST.get('txt_qualification')
        teacher.teacher_address = request.POST.get('txt_address')

        if request.FILES.get('file_photo'):
            teacher.teacher_photo = request.FILES.get('file_photo')

        teacher.save()
        request.session['tname'] = teacher.teacher_name
        messages.success(request, "Profile updated successfully!")
        return redirect('Teacher:my_profile')

    return render(request, 'Teacher/EditProfile.html', {'teacher': teacher})

# ==============================================================================
# 3. CHANGE PASSWORD
# ==============================================================================
def ChangePassword(request):
    if not check_teacher_session(request):
        return redirect('Guest:login')

    teacher = tbl_teacher.objects.get(id=request.session['tid'])

    if request.method == "POST":
        current_pass = request.POST.get('txt_curr_pass')
        new_pass = request.POST.get('txt_new_pass')
        confirm_pass = request.POST.get('txt_confirm_pass')

        if teacher.teacher_password != current_pass:
            messages.error(request, "Current password does not match!")
        elif new_pass != confirm_pass:
            messages.error(request, "New passwords do not match!")
        else:
            teacher.teacher_password = new_pass
            teacher.save()
            messages.success(request, "Password changed successfully!")
            return redirect('Teacher:my_profile')

    return render(request, 'Teacher/ChangePassword.html')

# ==============================================================================
# 4. VIEW TIMETABLE (Teacher Specific Timetable Across Monday-Friday)
# ==============================================================================
def ViewTimetable(request):
    if not check_teacher_session(request):
        return redirect('Guest:login')

    teacher = tbl_teacher.objects.get(id=request.session['tid'])
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [1, 2, 3, 4, 5]

    tt_entries = tbl_timetable.objects.filter(assign_subject__teacher=teacher).select_related('assign_subject__subject', 'semester')
    tt_map = {(entry.day, entry.period): entry for entry in tt_entries}

    timetable_matrix = []
    for day in days:
        row = {'day': day, 'slots': []}
        for period in periods:
            row['slots'].append(tt_map.get((day, period), None))
        timetable_matrix.append(row)

    return render(request, 'Teacher/ViewTimetable.html', {
        'teacher': teacher,
        'timetable_matrix': timetable_matrix,
        'periods': periods
    })

# ==============================================================================
# 5. QR CODE GENERATE & PROJECT (Dynamic QR Code refreshes every 5 seconds)
# ==============================================================================
def SelectPeriodForQR(request):
    """Teacher selects today's class period or any assigned subject to start QR Attendance."""
    if not check_teacher_session(request):
        return redirect('Guest:login')

    teacher = tbl_teacher.objects.get(id=request.session['tid'])
    today_name = datetime.date.today().strftime('%A')

    # Today's timetable slots
    today_slots = tbl_timetable.objects.filter(
        assign_subject__teacher=teacher,
        day=today_name
    ).select_related('semester', 'assign_subject__subject')

    # All assigned subjects as backup
    all_assigned = tbl_assign_subject.objects.filter(teacher=teacher).select_related('subject', 'subject__semester')

    return render(request, 'Teacher/SelectPeriodForQR.html', {
        'today_name': today_name,
        'today_slots': today_slots,
        'all_assigned': all_assigned
    })


def GenerateQRCode(request, assign_id):
    """
    Teacher presentation view that displays the dynamic QR code on screen.
    The client-side JavaScript calls get_dynamic_token every 5 seconds to reload the QR code.
    """
    if not check_teacher_session(request):
        return redirect('Guest:login')

    assign_obj = get_object_or_404(tbl_assign_subject, id=assign_id)
    today = datetime.date.today()

    # Get or create active QR Session for today
    session_obj, created = tbl_qrsession.objects.get_or_create(
        assign_subject=assign_obj,
        session_date=today,
        is_active=True,
        defaults={'current_token': str(uuid.uuid4())}
    )

    return render(request, 'Teacher/GenerateQRCode.html', {
        'assign': assign_obj,
        'session_obj': session_obj
    })


def GetDynamicToken(request, session_id):
    """
    API endpoint: Updates token every 5 seconds and returns current token and attendance count.
    Called via AJAX from Teacher's projector screen.
    """
    try:
        session_obj = tbl_qrsession.objects.get(id=session_id, is_active=True)
        # Generate new 12-char secure dynamic random code
        new_token = uuid.uuid4().hex[:12].upper()
        session_obj.current_token = new_token
        session_obj.save()

        # Count students marked today
        present_count = tbl_attendance.objects.filter(qrsession=session_obj).count()

        return JsonResponse({
            'status': 'success',
            'session_id': session_obj.id,
            'token': new_token,
            'present_count': present_count,
            'updated_at': datetime.datetime.now().strftime('%H:%M:%S')
        })
    except tbl_qrsession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session ended or not found.'}, status=404)


def RenderQRImage(request, token):
    """
    Generates a PNG QR Code on the fly for the dynamic token string.
    """
    # The payload embedded in the QR contains: IMCA-ATTENDANCE:<TOKEN>
    qr_data = f"IMCA-ATTENDANCE:{token}"
    img = qrcode.make(qr_data)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def CloseQRSession(request, session_id):
    """Teacher closes the attendance session."""
    if not check_teacher_session(request):
        return redirect('Guest:login')

    session_obj = get_object_or_404(tbl_qrsession, id=session_id)
    session_obj.is_active = False
    session_obj.save()
    messages.success(request, "QR Attendance session successfully closed.")
    return redirect('Teacher:view_attendance')

# ==============================================================================
# 6. VIEW ATTENDANCE OF STUDENTS
# ==============================================================================
def ViewAttendance(request):
    """
    Teacher views attendance logs of students across their assigned subjects.
    """
    if not check_teacher_session(request):
        return redirect('Guest:login')

    teacher = tbl_teacher.objects.get(id=request.session['tid'])
    assigned_subjects = tbl_assign_subject.objects.filter(teacher=teacher).select_related('subject', 'subject__semester')

    selected_assign_id = request.GET.get('assign_id')
    selected_date = request.GET.get('date') or str(datetime.date.today())

    attendances = []
    selected_assign = None

    if selected_assign_id:
        selected_assign = tbl_assign_subject.objects.filter(id=selected_assign_id, teacher=teacher).first()
        if selected_assign:
            attendances = tbl_attendance.objects.filter(
                qrsession__assign_subject=selected_assign,
                attendance_date=selected_date
            ).select_related('student', 'student__semester', 'qrsession').order_by('student__student_rollno')

    return render(request, 'Teacher/ViewAttendance.html', {
        'teacher': teacher,
        'assigned_subjects': assigned_subjects,
        'selected_assign': selected_assign,
        'selected_assign_id': selected_assign_id,
        'selected_date': selected_date,
        'attendances': attendances,
    })
