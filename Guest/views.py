from django.shortcuts import render, redirect
from Administrator.models import tbl_admin, tbl_teacher, tbl_student, tbl_semester
from django.contrib import messages

# ==============================================================================
# GUEST VIEWS: HOMEPAGE, LOGIN, REGISTRATION, LOGOUT
# ==============================================================================

def HomePage(request):
    """Landing homepage for Nirmala IMCA portal."""
    return render(request, 'Guest/HomePage.html')


def Login(request):
    """
    Unified Login View:
    Handles Admin, Teacher, and Student login with role redirection.
    """
    if request.method == "POST":
        email = request.POST.get('txt_email')
        password = request.POST.get('txt_password')
        role = request.POST.get('sel_role')

        # 1. Admin Login
        if role == "Admin":
            admin = tbl_admin.objects.filter(admin_email=email, admin_password=password).first()
            if admin:
                request.session['aid'] = admin.id
                request.session['aname'] = admin.admin_name
                request.session['role'] = 'Admin'
                return redirect('Administrator:admin_dashboard')
            else:
                messages.error(request, "Invalid Admin Credentials!")

        # 2. Teacher Login
        elif role == "Teacher":
            teacher = tbl_teacher.objects.filter(teacher_email=email, teacher_password=password).first()
            if teacher:
                request.session['tid'] = teacher.id
                request.session['tname'] = teacher.teacher_name
                request.session['role'] = 'Teacher'
                return redirect('Teacher:teacher_dashboard')
            else:
                messages.error(request, "Invalid Teacher Credentials!")

        # 3. Student (User) Login
        elif role == "Student":
            student = tbl_student.objects.filter(student_email=email, student_password=password).first()
            if student:
                request.session['sid'] = student.id
                request.session['sname'] = student.student_name
                request.session['sem_id'] = student.semester_id
                request.session['role'] = 'Student'
                return redirect('Student:student_dashboard')
            else:
                messages.error(request, "Invalid Student Credentials!")

    return render(request, 'Guest/Login.html')


def UserRegistration(request):
    """
    Student / User Registration for IMCA.
    """
    semesters = tbl_semester.objects.all().order_by('semester_number')

    if request.method == "POST":
        name = request.POST.get('txt_name')
        email = request.POST.get('txt_email')
        contact = request.POST.get('txt_contact')
        rollno = request.POST.get('txt_rollno')
        address = request.POST.get('txt_address')
        semester_id = request.POST.get('sel_semester')
        password = request.POST.get('txt_password')
        photo = request.FILES.get('file_photo')

        # Check existing email or rollno
        if tbl_student.objects.filter(student_email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'Guest/UserRegistration.html', {'semesters': semesters})

        if tbl_student.objects.filter(student_rollno=rollno).exists():
            messages.error(request, "Roll Number already registered!")
            return render(request, 'Guest/UserRegistration.html', {'semesters': semesters})

        sem_obj = tbl_semester.objects.get(id=semester_id)
        tbl_student.objects.create(
            student_name=name,
            student_email=email,
            student_contact=contact,
            student_rollno=rollno,
            student_address=address,
            semester=sem_obj,
            student_password=password,
            student_photo=photo
        )
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('Guest:login')

    return render(request, 'Guest/UserRegistration.html', {'semesters': semesters})


def Logout(request):
    """Clear session data and redirect to login."""
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('Guest:login')
