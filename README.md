# 🎓 QR-Code Based Attendance & Timetable Generator (IMCA Department)

A full-stack Django application crafted for **Nirmala Integrated MCA (IMCA)** department, adhering strictly to the architecture and directory pattern observed in `D:\Nirmala_IMCA\DjangoMiniProject`.

---

## 🌟 Modules & Features Implemented

### 1. 👨‍💼 Administrator
- **1. Semester Management**: Create, view, and delete IMCA Semesters (1 through 10).
- **2. Subject Management**: Add subjects with subject codes linked directly to IMCA semesters.
- **3. Teacher Management**: Register faculty with email, phone, qualification, address, and profile pictures.
- **4. Assign Subject to Teacher**: Map faculties to semester subjects.
- **5. View Complaints**: Review student grievances and write official replies.
- **6. View Users**: List and search all enrolled IMCA students per semester.
- **7. Generate Timetable**:
  - **Auto-Generate Timetable**: Automatic conflict-free generator across Monday–Friday (5 periods/day) ensuring no teacher is double-booked across different semesters in the same slot.
  - **Manual Timetable Slotting**: Slot-by-slot override and custom scheduling with clash detection.

### 2. 🌐 Guest
- **1. Login**: Unified, role-aware authentication for Admin, Teacher, and Student.
- **2. User Registration**: Student registration with IMCA roll number, contact, semester selection, photo, and password.

### 3. 👨‍🏫 Teacher
- **1. My Profile**: View faculty profile, qualification, and contact details.
- **2. Edit Profile**: Update faculty information and upload photo.
- **3. Change Password**: Self-service secure password management.
- **4. View Timetable**: Weekly view of all assigned teaching periods (Monday–Friday).
- **5. Dynamic QR Code Generator (Every 5 Seconds)**:
  - Select scheduled period or any assigned subject.
  - Projects an auto-refreshing QR Code that **dynamically updates every 5 seconds** via AJAX to eliminate proxy attendance.
  - Live count of students scanning in real time.
- **6. View Attendance Of Students**: Filter attendance logs by subject and date to inspect student status.

### 4. 🎓 User / Student
- **1. My Profile**: View student roll number, semester, and personal details.
- **2. Edit Profile**: Update contact details, address, and profile photo.
- **3. Change Password**: Change student account password.
- **4. View Timetable**: 5-day timetable grid for the student's enrolled IMCA semester.
- **5. Scan QR & View Attendance**:
  - Live camera / mobile webcam QR code scanner (using HTML5 QR Scanner).
  - Instant validation of current dynamic token with real-time feedback.
  - Historical attendance verification and log.
- **6. Complaints**: Submit academic or attendance grievances directly to Admin and view replies.

---

## 🔑 Default Login Credentials

| Role | Email / Login ID | Password | Notes |
|---|---|---|---|
| **Admin** | `admin@imca.com` | `admin123` | Default Administrator |
| **Teacher (Demo)** | `ajith@nirmala.ac.in` | `password123` | Prof. Ajith Kumar |
| **Teacher (Demo)** | `priya@nirmala.ac.in` | `password123` | Dr. Priya Mathew |
| **Student (Demo)** | `rahul@imca.com` | `password123` | Rahul K S (Roll: IMCA202601) |

---

## 🚀 How to Run the Project

1. Open your terminal in this project root:
   ```powershell
   cd "d:\Nirmala_IMCA\QrBasedAttendance&TimetableGeneration"
   ```

2. Start the development server:
   ```powershell
   python manage.py runserver
   ```

3. Visit `http://127.0.0.1:8000/` in your browser.

