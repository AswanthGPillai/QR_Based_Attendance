from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from Administrator.models import (
    tbl_student, tbl_timetable, tbl_attendance,
    tbl_complaint, tbl_qrsession, tbl_semester
)
import datetime

# ==============================================================================
# Helper to check Student session
# ==============================================================================
def check_student_session(request):
    return 'sid' in request.session

# ==============================================================================
# STUDENT DASHBOARD
# ==============================================================================
def StudentDashboard(request):
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.select_related('semester').get(id=request.session['sid'])
    today_name = datetime.date.today().strftime('%A')
    today_classes = tbl_timetable.objects.filter(semester=student.semester, day=today_name).order_by('period')

    total_attended = tbl_attendance.objects.filter(student=student).count()
    total_complaints = tbl_complaint.objects.filter(student=student).count()

    context = {
        'student': student,
        'today_name': today_name,
        'today_classes': today_classes,
        'total_attended': total_attended,
        'total_complaints': total_complaints,
    }
    return render(request, 'Student/StudentDashboard.html', context)

# ==============================================================================
# 1. MY PROFILE
# ==============================================================================
def MyProfile(request):
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.select_related('semester').get(id=request.session['sid'])
    return render(request, 'Student/MyProfile.html', {'student': student})

# ==============================================================================
# 2. EDIT PROFILE
# ==============================================================================
def EditProfile(request):
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.get(id=request.session['sid'])

    if request.method == "POST":
        student.student_name = request.POST.get('txt_name')
        student.student_contact = request.POST.get('txt_contact')
        student.student_address = request.POST.get('txt_address')

        if request.FILES.get('file_photo'):
            student.student_photo = request.FILES.get('file_photo')

        student.save()
        request.session['sname'] = student.student_name
        messages.success(request, "Profile updated successfully!")
        return redirect('Student:my_profile')

    return render(request, 'Student/EditProfile.html', {'student': student})

# ==============================================================================
# 3. CHANGE PASSWORD
# ==============================================================================
def ChangePassword(request):
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.get(id=request.session['sid'])

    if request.method == "POST":
        current_pass = request.POST.get('txt_curr_pass')
        new_pass = request.POST.get('txt_new_pass')
        confirm_pass = request.POST.get('txt_confirm_pass')

        if student.student_password != current_pass:
            messages.error(request, "Current password does not match!")
        elif new_pass != confirm_pass:
            messages.error(request, "New passwords do not match!")
        else:
            student.student_password = new_pass
            student.save()
            messages.success(request, "Password changed successfully!")
            return redirect('Student:my_profile')

    return render(request, 'Student/ChangePassword.html')

# ==============================================================================
# 4. VIEW TIMETABLE (Student's Semester Timetable Across Mon-Fri)
# ==============================================================================
def ViewTimetable(request):
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.select_related('semester').get(id=request.session['sid'])
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [1, 2, 3, 4, 5]

    tt_entries = tbl_timetable.objects.filter(semester=student.semester).select_related('assign_subject__teacher', 'assign_subject__subject')
    tt_map = {(entry.day, entry.period): entry for entry in tt_entries}

    timetable_matrix = []
    for day in days:
        row = {'day': day, 'slots': []}
        for period in periods:
            row['slots'].append(tt_map.get((day, period), None))
        timetable_matrix.append(row)

    return render(request, 'Student/ViewTimetable.html', {
        'student': student,
        'timetable_matrix': timetable_matrix,
        'periods': periods
    })

# ==============================================================================
# SCAN QR & MARK ATTENDANCE
# ==============================================================================
def ScanQR(request):
    """
    Student opens camera / webcam scanner or inputs scanned dynamic token.
    Validates token in real-time against active tbl_qrsession.
    """
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.select_related('semester').get(id=request.session['sid'])
    today = datetime.date.today()

    if request.method == "POST":
        scanned_data = request.POST.get('txt_token', '').strip()

        # Handle prefix if present: "IMCA-ATTENDANCE:<TOKEN>"
        if scanned_data.startswith("IMCA-ATTENDANCE:"):
            token = scanned_data.split("IMCA-ATTENDANCE:")[1].strip()
        else:
            token = scanned_data

        # Check if matching active session exists for today
        active_session = tbl_qrsession.objects.filter(
            current_token=token,
            is_active=True,
            session_date=today
        ).first()

        if not active_session:
            messages.error(request, "❌ Invalid or expired QR Code! The code changes every 5 seconds. Please scan the current code.")
            return redirect('Student:scan_qr')

        # Check if student's semester matches the subject semester
        if active_session.assign_subject.subject.semester_id != student.semester_id:
            messages.error(request, f"⚠️ You belong to {student.semester.semester_name}, but this class is for {active_session.assign_subject.subject.semester.semester_name}.")
            return redirect('Student:scan_qr')

        # Check if student has already marked attendance today for this session
        existing_attendance = tbl_attendance.objects.filter(
            student=student,
            qrsession=active_session,
            attendance_date=today
        ).first()

        if existing_attendance:
            messages.warning(request, f"ℹ️ You have already marked attendance for {active_session.assign_subject.subject.subject_name} today!")
            return redirect('Student:view_attendance')

        # Mark attendance
        tbl_attendance.objects.create(
            student=student,
            qrsession=active_session,
            status='Present'
        )
        messages.success(request, f"🎉 Attendance marked successfully for {active_session.assign_subject.subject.subject_name}!")
        return redirect('Student:view_attendance')

    return render(request, 'Student/ScanQR.html', {'student': student})

# ==============================================================================
# 5. VIEW ATTENDANCE
# ==============================================================================
def ViewAttendance(request):
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.select_related('semester').get(id=request.session['sid'])
    attendances = tbl_attendance.objects.filter(student=student).select_related(
        'qrsession__assign_subject__subject',
        'qrsession__assign_subject__teacher'
    ).order_by('-attendance_date', '-attendance_time')

    total_present = attendances.count()

    return render(request, 'Student/ViewAttendance.html', {
        'student': student,
        'attendances': attendances,
        'total_present': total_present,
    })

# ==============================================================================
# 6. COMPLAINTS (Submit Grievance & View Admin Replies)
# ==============================================================================
def Complaints(request):
    if not check_student_session(request):
        return redirect('Guest:login')

    student = tbl_student.objects.get(id=request.session['sid'])
    complaints = tbl_complaint.objects.filter(student=student).order_by('-id')

    if request.method == "POST":
        title = request.POST.get('txt_title')
        content = request.POST.get('txt_content')

        tbl_complaint.objects.create(
            student=student,
            complaint_title=title,
            complaint_content=content
        )
        messages.success(request, "Your complaint/query has been submitted to the Admin.")
        return redirect('Student:complaints')

    return render(request, 'Student/Complaints.html', {
        'student': student,
        'complaints': complaints
    })
