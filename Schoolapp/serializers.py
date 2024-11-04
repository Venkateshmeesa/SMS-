from rest_framework import serializers
from .models import *


class AdminPrincipalRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPrincipalRegistration
        fields = '__all__'


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    class_assigned = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())

    class Meta:
        model = StudentEnrollment
        fields = '__all__'


class StaffEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffEnrollment
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    enrollment = StudentEnrollmentSerializer()

    class Meta:
        model = StudentProfile
        fields = '__all__'


class StaffProfileSerializer(serializers.ModelSerializer):
    enrollment = StaffEnrollmentSerializer()

    class Meta:
        model = StaffProfile
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class_assigned = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    staff_assigned = serializers.PrimaryKeyRelatedField(queryset=StaffProfile.objects.all())

    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'marks', 'subject_code', 'staff_assigned', 'class_assigned']

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'

class ClasswiseFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasswiseFee
        fields = ['class_name', 'Fee']

class StudentFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFee
        fields = ['student', 'Fee', 'amount_paid', 'amount_due', 'installments', 'due_date', 'date_of_payment']


class StaffSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSalary
        fields = '__all__'


class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = '__all__'


class StaffAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAttendance
        fields = '__all__'


class StudentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeedback
        fields = '__all__'


class StaffFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffFeedback
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class ExtracurricularActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtracurricularActivity
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class ClassTimetableSerializer(serializers.ModelSerializer):
    class_assigned = ClassSerializer()
    subject = SubjectSerializer()
    staff = StaffEnrollmentSerializer()

    class Meta:
        model = ClassTimetable
        fields = '__all__'


class ExaminationTimetableSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    class_assigned = ClassSerializer()

    class Meta:
        model = ExaminationTimetable
        fields = '__all__'


class CounselingSessionSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer()
    counselor = StaffProfileSerializer()

    class Meta:
        model = CounselingSession
        fields = '__all__'


class BehaviorReportSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer()

    class Meta:
        model = BehaviorReport
        fields = '__all__'


class CertificateRequestsStudentSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer()

    class Meta:
        model = CertificateRequestsStudent
        fields = '__all__'
