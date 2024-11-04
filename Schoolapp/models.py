from django.db import models

class AdminPrincipalRegistration(models.Model):
    admin_name = models.CharField(max_length=50)
    admin_id = models.CharField(unique=True, max_length=100)
    pwd = models.CharField(max_length=50)

    def __str__(self):
        return self.admin_name


class Class(models.Model):
    class_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.class_name


class StudentEnrollment(models.Model):
    student_first_name = models.CharField(max_length=255)
    student_last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    student_id = models.CharField(unique=True, max_length=255)
    religion = models.CharField(max_length=50)
    caste = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=50)
    student_pwd = models.CharField(max_length=255)
    student_email = models.EmailField(max_length=254)
    student_aadhar = models.FileField(upload_to='documents/', null=True)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    guardian_name = models.CharField(max_length=50)
    guardian_email = models.EmailField(max_length=254)
    guardian_mobile = models.CharField(max_length=15)
    guardian_whatsapp = models.CharField(max_length=15)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.PositiveIntegerField()
    parent_aadhar = models.FileField(upload_to='documents/', null=True)
    previous_school_name = models.CharField(max_length=100)
    previous_school_address = models.CharField(max_length=100)
    previous_school_document = models.FileField(upload_to='documents/', null=True)
    health_information = models.CharField(max_length=500)
    health_information_document = models.FileField(upload_to='documents/', null=True)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    gender = models.BooleanField(choices=[(True, 'Male'), (False, 'Female')])


class StaffEnrollment(models.Model):
    staff_name = models.CharField(max_length=255)
    mobile_and_whatsapp = models.BigIntegerField()
    staff_id = models.CharField(unique=True, max_length=255)
    staff_image = models.ImageField(upload_to='staff_img/')
    father_name = models.CharField(max_length=50)
    staff_aadhar = models.BigIntegerField()
    staff_gender = models.BooleanField(choices=[(True, 'Male'), (False, 'Female')])
    staff_pwd = models.CharField(max_length=255)
    date_of_hire = models.DateField()
    designation = models.CharField(max_length=255)
    category = models.BooleanField(choices=[(True, 'Teaching Staff'), (False, 'Non-Teaching Staff')])
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    experience = models.IntegerField()
    date_of_birth = models.DateField()
    staff_email = models.EmailField()


class StudentProfile(models.Model):
    enrollment = models.OneToOneField(StudentEnrollment, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField()
    address = models.TextField()
    image = models.ImageField(upload_to='student_img/')
    contact_number = models.CharField(max_length=15)


class StaffProfile(models.Model):
    enrollment = models.OneToOneField(StaffEnrollment, on_delete=models.CASCADE, related_name='profile')
    experience_in_years = models.IntegerField()
    image = models.ImageField(upload_to='staff_img/')
    address = models.TextField()
    date_of_birth = models.DateField()
    married_status = models.BooleanField(choices=[(True, 'Yes'), (False, 'No')])


class Subject(models.Model):
    subject_name = models.CharField(max_length=50)
    marks = models.IntegerField()
    subject_code = models.CharField(max_length=50)
    staff_assigned = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='subjects')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return self.subject_name

    class Meta:
        unique_together = ('subject_name', 'class_assigned')


class Parent(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='parent')
    contact_number = models.CharField(max_length=15)


class ClasswiseFee(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    Fee = models.IntegerField()



class StudentFee(models.Model):
    student = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='fees')
    Fee = models.ForeignKey(ClasswiseFee, on_delete=models.CASCADE )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    installments = models.IntegerField()
    due_date = models.DateField()
    date_of_payment = models.DateField()

    def __str__(self):
        return f"{self.student.student_first_name} {self.student.student_last_name} - Due: {self.amount_due}, Paid: {self.amount_paid}"


class StaffSalary(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='salaries')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()


class StaffAttendance(models.Model):
    staff = models.ForeignKey(StaffEnrollment, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    is_present = models.BooleanField(default=False)


class StudentAttendance(models.Model):
    student = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='attendance')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    is_present = models.BooleanField(default=False)


class StaffAttendanceReport(models.Model):
    staff = models.ForeignKey(StaffEnrollment, on_delete=models.CASCADE, related_name='attendance_reports')
    total_present_days = models.IntegerField()
    total_absent_days = models.IntegerField()


class StudentAttendanceReport(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_reports')
    attendance_date_range_start = models.DateField()
    attendance_date_range_end = models.DateField()
    total_present_days = models.IntegerField()
    total_absent_days = models.IntegerField()


class StaffLeaveReport(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='leave_reports')
    leave_start_date = models.DateField()
    leave_end_date = models.DateField()
    reason = models.TextField()


class StudentLeaveReport(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='leave_reports')
    leave_start_date = models.DateField()
    leave_end_date = models.DateField()
    reason = models.TextField()


class StudentFeedback(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_date = models.DateField()
    content = models.TextField()


class StaffFeedback(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_date = models.DateField()
    content = models.TextField()


class StudentGrade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    grade = models.CharField(max_length=2)
    date_recorded = models.DateField()


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
    participants = models.ManyToManyField(StudentProfile, blank=True, related_name='events')


class ExtracurricularActivity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    participants = models.ManyToManyField(StudentProfile, blank=True, related_name='activities')


class Notification(models.Model):
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class ClassTimetable(models.Model):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetable')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetables')
    staff = models.ForeignKey(StaffEnrollment, on_delete=models.CASCADE, related_name='timetables')
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()


class ExaminationTimetable(models.Model):
    name_of_exam = models.CharField(max_length=225)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams')


class CounselingSession(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='counseling_sessions')
    date = models.DateField()
    counselor = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, related_name='counseling_sessions')
    notes = models.TextField()


class BehaviorReport(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='behavior_reports')
    report_date = models.DateField()
    description = models.TextField()
    action_taken = models.TextField()


class CertificateRequestsStudent(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='certificate_requests')
    certificate_type = models.CharField(max_length=255)
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_type} requested by {self.student.student_first_name} {self.student.student_last_name} on {self.request_date}"
