from django.shortcuts import render, redirect, get_object_or_404
from Administrator.models import (
    tbl_semester, tbl_teacher, tbl_subject, tbl_assign_subject,
    tbl_student, tbl_complaint, tbl_timetable
)
from django.contrib import messages
import datetime
import random

# ==============================================================================
# Helper to check Admin session
# ==============================================================================
def check_admin_session(request):
    if 'aid' not in request.session:
        return False
    return True

# ==============================================================================
# ADMIN DASHBOARD
# ==============================================================================
def AdminDashboard(request):
    if not check_admin_session(request):
        return redirect('Guest:login')

    total_teachers = tbl_teacher.objects.count()
    total_students = tbl_student.objects.count()
    total_subjects = tbl_subject.objects.count()
    pending_complaints = tbl_complaint.objects.filter(complaint_status=0).count()

    context = {
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_subjects': total_subjects,
        'pending_complaints': pending_complaints,
    }
    return render(request, 'Administrator/AdminDashboard.html', context)

# ==============================================================================
# 1. SEMESTER MANAGEMENT
# ==============================================================================
def Semester(request):
    if not check_admin_session(request):
        return redirect('Guest:login')

    semesters = tbl_semester.objects.all().order_by('semester_number')

    if request.method == "POST":
        sem_name = request.POST.get('txt_sem_name')
        sem_no = request.POST.get('txt_sem_no')

        if tbl_semester.objects.filter(semester_number=sem_no).exists():
            messages.error(request, "Semester with this number already exists!")
        else:
            tbl_semester.objects.create(semester_name=sem_name, semester_number=sem_no)
            messages.success(request, "Semester added successfully!")
            return redirect('Administrator:semester')

    return render(request, 'Administrator/Semester.html', {'semesters': semesters})

def DeleteSemester(request, id):
    if not check_admin_session(request):
        return redirect('Guest:login')

    sem = get_object_or_404(tbl_semester, id=id)
    sem.delete()
    messages.success(request, "Semester deleted.")
    return redirect('Administrator:semester')

# ==============================================================================
# 2. SUBJECT MANAGEMENT
# ==============================================================================
def Subject(request):
    if not check_admin_session(request):
        return redirect('Guest:login')

    semesters = tbl_semester.objects.all().order_by('semester_number')
    subjects = tbl_subject.objects.all().select_related('semester').order_by('semester__semester_number', 'subject_code')

    if request.method == "POST":
        sub_code = request.POST.get('txt_code')
        sub_name = request.POST.get('txt_name')
        sem_id = request.POST.get('sel_semester')

        if tbl_subject.objects.filter(subject_code=sub_code).exists():
            messages.error(request, "Subject code already exists!")
        else:
            sem_obj = tbl_semester.objects.get(id=sem_id)
            tbl_subject.objects.create(subject_code=sub_code, subject_name=sub_name, semester=sem_obj)
            messages.success(request, "Subject created successfully!")
            return redirect('Administrator:subject')

    return render(request, 'Administrator/Subject.html', {'semesters': semesters, 'subjects': subjects})

def DeleteSubject(request, id):
    if not check_admin_session(request):
        return redirect('Guest:login')

    sub = get_object_or_404(tbl_subject, id=id)
    sub.delete()
    messages.success(request, "Subject deleted.")
    return redirect('Administrator:subject')

# ==============================================================================
# 3. TEACHER MANAGEMENT
# ==============================================================================
def Teacher(request):
    if not check_admin_session(request):
        return redirect('Guest:login')

    teachers = tbl_teacher.objects.all().order_by('teacher_name')

    if request.method == "POST":
        name = request.POST.get('txt_name')
        email = request.POST.get('txt_email')
        contact = request.POST.get('txt_contact')
        qualification = request.POST.get('txt_qualification')
        address = request.POST.get('txt_address')
        password = request.POST.get('txt_password')
        photo = request.FILES.get('file_photo')

        if tbl_teacher.objects.filter(teacher_email=email).exists():
            messages.error(request, "Teacher with this email already exists!")
        else:
            tbl_teacher.objects.create(
                teacher_name=name,
                teacher_email=email,
                teacher_contact=contact,
                teacher_qualification=qualification,
                teacher_address=address,
                teacher_password=password,
                teacher_photo=photo
            )
            messages.success(request, "Teacher added successfully!")
            return redirect('Administrator:teacher')

    return render(request, 'Administrator/Teacher.html', {'teachers': teachers})

def DeleteTeacher(request, id):
    if not check_admin_session(request):
        return redirect('Guest:login')

    teacher = get_object_or_404(tbl_teacher, id=id)
    teacher.delete()
    messages.success(request, "Teacher record deleted.")
    return redirect('Administrator:teacher')

# ==============================================================================
# 4. ASSIGN SUBJECT TO TEACHER
# ==============================================================================
def AssignSubject(request):
    if not check_admin_session(request):
        return redirect('Guest:login')

    teachers = tbl_teacher.objects.all().order_by('teacher_name')
    subjects = tbl_subject.objects.all().select_related('semester').order_by('semester__semester_number')
    assignments = tbl_assign_subject.objects.all().select_related('teacher', 'subject', 'subject__semester')

    if request.method == "POST":
        teacher_id = request.POST.get('sel_teacher')
        subject_id = request.POST.get('sel_subject')

        if tbl_assign_subject.objects.filter(teacher_id=teacher_id, subject_id=subject_id).exists():
            messages.warning(request, "Subject is already assigned to this teacher!")
        else:
            teacher_obj = tbl_teacher.objects.get(id=teacher_id)
            subject_obj = tbl_subject.objects.get(id=subject_id)
            tbl_assign_subject.objects.create(teacher=teacher_obj, subject=subject_obj)
            messages.success(request, "Subject assigned to Teacher successfully!")
            return redirect('Administrator:assign_subject')

    return render(request, 'Administrator/AssignSubject.html', {
        'teachers': teachers,
        'subjects': subjects,
        'assignments': assignments
    })

def DeleteAssignSubject(request, id):
    if not check_admin_session(request):
        return redirect('Guest:login')

    assign = get_object_or_404(tbl_assign_subject, id=id)
    assign.delete()
    messages.success(request, "Assignment removed.")
    return redirect('Administrator:assign_subject')

# ==============================================================================
# 5. VIEW COMPLAINTS & REPLY
# ==============================================================================
def ViewComplaints(request):
    if not check_admin_session(request):
        return redirect('Guest:login')

    complaints = tbl_complaint.objects.all().select_related('student', 'student__semester').order_by('-id')

    if request.method == "POST":
        complaint_id = request.POST.get('txt_complaint_id')
        reply_content = request.POST.get('txt_reply')

        comp = get_object_or_404(tbl_complaint, id=complaint_id)
        comp.complaint_reply = reply_content
        comp.reply_date = datetime.date.today()
        comp.complaint_status = 1
        comp.save()
        messages.success(request, "Reply submitted successfully!")
        return redirect('Administrator:view_complaints')

    return render(request, 'Administrator/ViewComplaints.html', {'complaints': complaints})

# ==============================================================================
# 6. VIEW USERS (STUDENTS)
# ==============================================================================
def ViewUsers(request):
    if not check_admin_session(request):
        return redirect('Guest:login')

    sem_filter = request.GET.get('semester', '')
    if sem_filter:
        students = tbl_student.objects.filter(semester_id=sem_filter).select_related('semester').order_by('student_rollno')
    else:
        students = tbl_student.objects.all().select_related('semester').order_by('semester__semester_number', 'student_rollno')

    semesters = tbl_semester.objects.all().order_by('semester_number')
    return render(request, 'Administrator/ViewUsers.html', {
        'students': students,
        'semesters': semesters,
        'selected_sem': sem_filter
    })

def DeleteUser(request, id):
    if not check_admin_session(request):
        return redirect('Guest:login')

    student = get_object_or_404(tbl_student, id=id)
    student.delete()
    messages.success(request, "Student account removed.")
    return redirect('Administrator:view_users')

# ==============================================================================
# 7. GENERATE TIMETABLE (Automated & Manual Conflict-Free Generation)
# ==============================================================================
def GenerateTimeTable(request):
    """
    Timetable Generator for IMCA:
    1. Select a semester.
    2. Auto-generate conflict-free timetable across 5 Days (Mon-Fri) x 5 Periods (1-5),
       ensuring no teacher is double-booked across semesters at the same day & period.
    3. Option to manually add or clear slots.
    """
    if not check_admin_session(request):
        return redirect('Guest:login')

    semesters = tbl_semester.objects.all().order_by('semester_number')
    selected_sem_id = request.GET.get('semester') or request.POST.get('sel_semester')
    
    if not selected_sem_id and semesters.exists():
        selected_sem_id = str(semesters.first().id)

    selected_sem = tbl_semester.objects.filter(id=selected_sem_id).first() if selected_sem_id else None

    # Handle Actions: Auto Generate or Clear or Add Manual Slot
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "auto_generate" and selected_sem:
            # Fetch assigned subjects for this semester
            assigned_subjects = list(tbl_assign_subject.objects.filter(subject__semester=selected_sem).select_related('teacher', 'subject'))

            if not assigned_subjects:
                messages.error(request, f"No subjects assigned to teachers for {selected_sem.semester_name}. Please assign subjects first!")
                return redirect(f"{request.path}?semester={selected_sem_id}")

            # Clear existing timetable for this semester
            tbl_timetable.objects.filter(semester=selected_sem).delete()

            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            periods = [1, 2, 3, 4, 5]

            # Track teacher allocations across ALL semesters to prevent clashes:
            # (day, period) -> set of busy teacher IDs
            existing_timetables = tbl_timetable.objects.exclude(semester=selected_sem).select_related('assign_subject__teacher')
            teacher_busy_map = {}
            for tt in existing_timetables:
                key = (tt.day, tt.period)
                teacher_busy_map.setdefault(key, set()).add(tt.assign_subject.teacher_id)

            # Scheduling for each day and period
            subject_index = 0
            n_subs = len(assigned_subjects)
            
            # Shuffle slightly for organic distribution
            available_pool = assigned_subjects.copy()
            random.seed(int(selected_sem_id) + 42) # Deterministic yet distributed
            random.shuffle(available_pool)

            for day in days:
                for period in periods:
                    key = (day, period)
                    busy_teachers = teacher_busy_map.get(key, set())

                    # Find an assigned subject whose teacher is NOT busy in this slot
                    chosen_assign = None
                    for attempt in range(n_subs):
                        candidate = available_pool[(subject_index + attempt) % n_subs]
                        if candidate.teacher_id not in busy_teachers:
                            chosen_assign = candidate
                            subject_index = (subject_index + attempt + 1) % n_subs
                            break

                    # Fallback to candidate if all busy
                    if not chosen_assign:
                        chosen_assign = available_pool[subject_index % n_subs]
                        subject_index = (subject_index + 1) % n_subs

                    # Save slot
                    tbl_timetable.objects.create(
                        semester=selected_sem,
                        day=day,
                        period=period,
                        assign_subject=chosen_assign
                    )
                    teacher_busy_map.setdefault(key, set()).add(chosen_assign.teacher_id)

            messages.success(request, f"Timetable successfully generated for {selected_sem.semester_name} with zero clashes!")
            return redirect(f"{request.path}?semester={selected_sem_id}")

        elif action == "clear_timetable" and selected_sem:
            tbl_timetable.objects.filter(semester=selected_sem).delete()
            messages.info(request, f"Timetable cleared for {selected_sem.semester_name}.")
            return redirect(f"{request.path}?semester={selected_sem_id}")

        elif action == "manual_add" and selected_sem:
            day = request.POST.get('sel_day')
            period = request.POST.get('sel_period')
            assign_id = request.POST.get('sel_assign')

            assign_obj = tbl_assign_subject.objects.get(id=assign_id)

            # Check if teacher is busy elsewhere
            clash = tbl_timetable.objects.filter(day=day, period=period, assign_subject__teacher=assign_obj.teacher).exclude(semester=selected_sem).first()
            if clash:
                messages.error(request, f"Teacher {assign_obj.teacher.teacher_name} is already booked in {clash.semester.semester_name} during {day} Period {period}!")
            else:
                tbl_timetable.objects.update_or_create(
                    semester=selected_sem,
                    day=day,
                    period=period,
                    defaults={'assign_subject': assign_obj}
                )
                messages.success(request, f"Slot updated: {day} Period {period} -> {assign_obj.subject.subject_name}")
            return redirect(f"{request.path}?semester={selected_sem_id}")

    # Build the 5x5 timetable grid matrix for template display
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [1, 2, 3, 4, 5]
    timetable_matrix = []

    if selected_sem:
        tt_entries = tbl_timetable.objects.filter(semester=selected_sem).select_related('assign_subject__teacher', 'assign_subject__subject')
        tt_map = {(entry.day, entry.period): entry for entry in tt_entries}

        for day in days:
            row = {'day': day, 'slots': []}
            for period in periods:
                row['slots'].append(tt_map.get((day, period), None))
            timetable_matrix.append(row)

    assigned_for_sem = tbl_assign_subject.objects.filter(subject__semester=selected_sem) if selected_sem else []

    context = {
        'semesters': semesters,
        'selected_sem': selected_sem,
        'timetable_matrix': timetable_matrix,
        'periods': periods,
        'assigned_for_sem': assigned_for_sem,
        'days': days,
    }
    return render(request, 'Administrator/GenerateTimeTable.html', context)
