from django.db import models

# ==============================================================================
# 1. SEMESTER MODEL (Specifically for IMCA Department)
# ==============================================================================
class tbl_semester(models.Model):
    semester_name = models.CharField(max_length=50) # e.g., Semester 1, Semester 2...
    semester_number = models.IntegerField()        # 1 to 10 for IMCA

    def __str__(self):
        return f"IMCA {self.semester_name}"

# ==============================================================================
# 2. TEACHER MODEL
# ==============================================================================
class tbl_teacher(models.Model):
    teacher_name = models.CharField(max_length=100)
    teacher_email = models.EmailField(unique=True)
    teacher_contact = models.CharField(max_length=15)
    teacher_address = models.TextField()
    teacher_qualification = models.CharField(max_length=100, default='MCA / M.Tech')
    teacher_photo = models.FileField(upload_to='TeacherPhotos/', null=True, blank=True)
    teacher_password = models.CharField(max_length=50)

    def __str__(self):
        return self.teacher_name

# ==============================================================================
# 3. SUBJECT MODEL
# ==============================================================================
class tbl_subject(models.Model):
    subject_code = models.CharField(max_length=20) # e.g. IMCA101
    subject_name = models.CharField(max_length=100)
    semester = models.ForeignKey(tbl_semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"

# ==============================================================================
# 4. ASSIGN SUBJECT TO TEACHER
# ==============================================================================
class tbl_assign_subject(models.Model):
    teacher = models.ForeignKey(tbl_teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(tbl_subject, on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.teacher_name} - {self.subject.subject_name}"

# ==============================================================================
# 5. STUDENT / USER MODEL (IMCA Students)
# ==============================================================================
class tbl_student(models.Model):
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField(unique=True)
    student_contact = models.CharField(max_length=15)
    student_rollno = models.CharField(max_length=30, unique=True)
    student_address = models.TextField()
    semester = models.ForeignKey(tbl_semester, on_delete=models.CASCADE)
    student_photo = models.FileField(upload_to='StudentPhotos/', null=True, blank=True)
    student_password = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_name} ({self.student_rollno})"

# ==============================================================================
# 6. TIMETABLE MODEL
# Day of week (Monday to Friday) and Periods (1 to 5)
# ==============================================================================
class tbl_timetable(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    semester = models.ForeignKey(tbl_semester, on_delete=models.CASCADE)
    day = models.CharField(max_length=15, choices=DAY_CHOICES)
    period = models.IntegerField() # Period 1, 2, 3, 4, 5
    assign_subject = models.ForeignKey(tbl_assign_subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('semester', 'day', 'period')

    def __str__(self):
        return f"{self.semester.semester_name} - {self.day} P{self.period}: {self.assign_subject.subject.subject_name}"

# ==============================================================================
# 7. QR CODE SESSION MODEL (Teacher Generates Dynamic QR every 5s)
# ==============================================================================
class tbl_qrsession(models.Model):
    assign_subject = models.ForeignKey(tbl_assign_subject, on_delete=models.CASCADE)
    timetable = models.ForeignKey(tbl_timetable, on_delete=models.CASCADE, null=True, blank=True)
    session_date = models.DateField(auto_now_add=True)
    current_token = models.CharField(max_length=64)  # Dynamic rotating code
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QR Session - {self.assign_subject.subject.subject_name} on {self.session_date}"

# ==============================================================================
# 8. ATTENDANCE MODEL
# ==============================================================================
class tbl_attendance(models.Model):
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    qrsession = models.ForeignKey(tbl_qrsession, on_delete=models.CASCADE)
    attendance_date = models.DateField(auto_now_add=True)
    attendance_time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Present')

    class Meta:
        unique_together = ('student', 'qrsession', 'attendance_date')

    def __str__(self):
        return f"{self.student.student_name} - {self.attendance_date} ({self.status})"

# ==============================================================================
# 9. COMPLAINT MODEL
# ==============================================================================
class tbl_complaint(models.Model):
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    complaint_title = models.CharField(max_length=200)
    complaint_content = models.TextField()
    complaint_date = models.DateField(auto_now_add=True)
    complaint_reply = models.TextField(null=True, blank=True)
    reply_date = models.DateField(null=True, blank=True)
    complaint_status = models.IntegerField(default=0) # 0: Pending, 1: Replied

    def __str__(self):
        return f"Complaint by {self.student.student_name}: {self.complaint_title}"

# ==============================================================================
# 10. ADMIN MODEL
# ==============================================================================
class tbl_admin(models.Model):
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_password = models.CharField(max_length=50)

    def __str__(self):
        return self.admin_name
