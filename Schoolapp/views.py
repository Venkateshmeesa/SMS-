from rest_framework import viewsets, permissions, status
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

from rest_framework import viewsets
from rest_framework.response import Response
from .models import AdminPrincipalRegistration
from .serializers import AdminPrincipalRegistrationSerializer

class AdminPrincipalRegistrationView(viewsets.ModelViewSet):
    queryset = AdminPrincipalRegistration.objects.all()
    serializer_class = AdminPrincipalRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
class AdminLoginView(generics.GenericAPIView):
    """
    View for handling admin login and returning a JWT token.
    """
    def post(self, request, *args, **kwargs):
        admin_id = request.data.get('admin_id')
        password = request.data.get('pwd')
        
        try:
            # Attempt to retrieve the admin by admin_id
            admin = AdminPrincipalRegistration.objects.get(admin_id=admin_id)
            
            # Check if the password matches
            if admin.pwd == password:
                # Successful authentication, create tokens
                refresh = RefreshToken.for_user(admin)
                return Response({
                    'message': 'Login successful',
                    'admin_id': admin_id,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Invalid admin ID or password'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except AdminPrincipalRegistration.DoesNotExist:
            return Response({
                'message': 'Invalid admin ID or password'
            }, status=status.HTTP_401_UNAUTHORIZED)



class ClassViewSet(viewsets.ViewSet):
# GET /api/classes/ - List all classes
# POST /api/classes/ - Create a new class
# GET /api/classes/{id}/ - Retrieve a specific class
# PUT/PATCH /api/classes/{id}/ - Update a specific class
# DELETE /api/classes/{id}/ - Delete a specific class
    """
     simple ViewSet for managing classes.
    """

    def list(self, request):
        classes = Class.objects.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)

    def create(self, request):
        class_name = request.data.get('class_name')
        if Class.objects.filter(class_name=class_name).exists():
            return Response({"error": "Class with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            class_instance = Class.objects.get(pk=pk)
            serializer = ClassSerializer(class_instance)
            return Response(serializer.data)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            class_instance = Class.objects.get(pk=pk)
            serializer = ClassSerializer(class_instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            class_instance = Class.objects.get(pk=pk)
            class_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)

    
class ClassStudentsViewSet(viewsets.ViewSet):
    """
    A ViewSet for retrieving students in a specific class.
    """
    def get_students(self, request, pk=None):
        """
        Retrieve all students in a specific class by its ID.
        """
        print(f"Request received for class ID: {pk}")  # Debug output
        try:
            class_instance = Class.objects.get(pk=pk)
            students = StudentProfile.objects.filter(class_assigned=class_instance)

            if not students.exists():
                return Response({"message": "No students found in this class."}, status=status.HTTP_200_OK)

            serializer = StudentProfileSerializer(students, many=True)
            return Response(serializer.data)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)


class SubjectViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing subjects for each class.
    """

    def list(self, request, class_id=None):
        """
        Retrieve all subjects for a specific class by its ID.
        """
        try:
            class_instance = Class.objects.get(pk=class_id)
            subjects = Subject.objects.filter(class_assigned=class_instance)

            formatted_data = []
            for subject in subjects:
                formatted_data.append({
                    'Class': class_instance.class_name,
                    'Subject': subject.subject_name,
                    'Teacher': subject.staff_assigned.enrollment.name,  # Adjust based on your model
                    'Marks': subject.marks,
                    # 'Actions': '',  # You can add any action links or buttons if needed
                })

            return Response(formatted_data)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=404)

class StaffEnrollmentViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for managing staff enrollments, accessible only to admin users.
    """

    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        """
        Retrieve a list of staff enrollments.
        """
        staff_enrollments = StaffEnrollment.objects.all()
        serializer = StaffEnrollmentSerializer(staff_enrollments, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new staff enrollment and a linked StaffProfile.
        """
        serializer = StaffEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            staff_enrollment = serializer.save()
            
            # Create a StaffProfile linked to the StaffEnrollment
            staff_profile_data = {
                'enrollment': staff_enrollment,
                'experience_in_years': request.data.get('experience_in_years', 0),  # Ensure to pass this data
                'image': request.data.get('staff_image'),  # Adjust as necessary
                'address': request.data.get('address', ''),  # Ensure to pass this data
                'date_of_birth': request.data.get('date_of_birth'),  # Ensure to pass this data
                'married_status': request.data.get('married_status', False),  # Ensure to pass this data
            }
            staff_profile_data.save()

            staff_profile_serializer = StaffProfileSerializer(data=staff_profile_data)
            if staff_profile_serializer.is_valid():
                staff_profile_serializer.save()
            else:
                return Response(staff_profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific staff enrollment by its ID.
        """
        staff_instance = self.get_staff_enrollment(pk)
        if staff_instance:
            serializer = StaffEnrollmentSerializer(staff_instance)
            return Response(serializer.data)
        return Response({'error': 'Staff enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        Update a specific staff enrollment.
        """
        staff_instance = self.get_staff_enrollment(pk)
        if staff_instance:
            serializer = StaffEnrollmentSerializer(staff_instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Staff enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        Delete a specific staff enrollment.
        """
        staff_instance = self.get_staff_enrollment(pk)
        if staff_instance:
            staff_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Staff enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

    def get_staff_enrollment(self, pk):
        """
        Helper method to retrieve a staff enrollment by ID.
        Returns None if not found.
        """
        try:
            return StaffEnrollment.objects.get(pk=pk)
        except StaffEnrollment.DoesNotExist:
            return None
        

class StudentEnrollmentViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing student enrollments, accessible only to admin users.
    """

    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        """
        Retrieve a list of student enrollments.
        """
        student_enrollments = StudentEnrollment.objects.all()
        serializer = StudentEnrollmentSerializer(student_enrollments, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new student enrollment and linked StudentProfile.
        """
        serializer = StudentEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            student_enrollment = serializer.save()
            profile_data = {
                'enrollment': student_enrollment,
                'date_of_birth': request.data.get('profile', {}).get('date_of_birth'),
                'address': request.data.get('profile', {}).get('address'),
                'image': request.data.get('profile', {}).get('image'),  # Assuming the file is being uploaded
                'contact_number': request.data.get('profile', {}).get('contact_number'),
            }
            profile_serializer = StudentProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific student enrollment by its ID.
        """
        try:
            student_instance = StudentEnrollment.objects.get(pk=pk)
            serializer = StudentEnrollmentSerializer(student_instance)
            return Response(serializer.data)
        except StudentEnrollment.DoesNotExist:
            return Response({'error': 'Student enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        Update a specific student enrollment.
        """
        try:
            student_instance = StudentEnrollment.objects.get(pk=pk)
            serializer = StudentEnrollmentSerializer(student_instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # Check for profile updates
                if 'profile' in request.data:
                    profile_data = request.data['profile']
                    profile_instance = student_instance.profile
                    for attr, value in profile_data.items():
                        setattr(profile_instance, attr, value)
                    profile_instance.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentEnrollment.DoesNotExist:
            return Response({'error': 'Student enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        Delete a specific student enrollment.
        """
        try:
            student_instance = StudentEnrollment.objects.get(pk=pk)
            student_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except StudentEnrollment.DoesNotExist:
            return Response({'error': 'Student enrollment not found'}, status=status.HTTP_404_NOT_FOUND)
    def retrieve_students_by_class(self, request, class_id=None):
        if class_id is None:
            return Response({'error': 'Class ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        students = StudentEnrollment.objects.filter(class_assigned__id=class_id)

        if not students.exists():
            return Response({"message": "No students found for this class."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentEnrollmentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SubjectViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing subjects for each class.
    """

    def list(self, request, class_id=None):
        """
        Retrieve all subjects for a specific class by its ID.
        """
        try:
            class_instance = Class.objects.get(pk=class_id)
            subjects = Subject.objects.filter(class_assigned=class_instance)

            serializer = SubjectSerializer(subjects, many=True)
            return Response(serializer.data)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, class_id=None):
        """
        Add a new subject for a specific class, ensuring no duplicates.
        """
        try:
            class_instance = Class.objects.get(pk=class_id)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)

        subject_name = request.data.get('subject_name')
        subject_code = request.data.get('subject_code')
        marks = request.data.get('marks')
        staff_id = request.data.get('staff_assigned')

        if Subject.objects.filter(subject_name=subject_name, class_assigned=class_instance).exists():
            return Response({"error": "Subject already exists for this class."}, status=status.HTTP_400_BAD_REQUEST)

        subject_data = {
            'subject_name': subject_name,
            'subject_code': subject_code,
            'marks': marks,
            'staff_assigned': staff_id,
            'class_assigned': class_instance.id,
        }

        serializer = SubjectSerializer(data=subject_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, class_id=None, pk=None):
        """
        Update an existing subject for a specific class.
        """
        try:
            class_instance = Class.objects.get(pk=class_id)
            subject_instance = Subject.objects.get(pk=pk, class_assigned=class_instance)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubjectSerializer(subject_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, class_id=None, pk=None):
        """
        Delete a specific subject for a class.
        """
        try:
            class_instance = Class.objects.get(pk=class_id)
            subject_instance = Subject.objects.get(pk=pk, class_assigned=class_instance)
            subject_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)



class ClasswiseFeeViewSet(viewsets.ViewSet):
    # permission_classes = [IsAdminUser]

    def list(self, request):
        """
        Retrieve a list of all class-wise fees.
        """
        fees = ClasswiseFee.objects.all()
        serializer = ClasswiseFeeSerializer(fees, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new class-wise fee.
        """
        serializer = ClasswiseFeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific class-wise fee by its ID.
        """
        try:
            fee = ClasswiseFee.objects.get(pk=pk)
            serializer = ClasswiseFeeSerializer(fee)
            return Response(serializer.data)
        except ClasswiseFee.DoesNotExist:
            return Response({'error': 'Classwise fee not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        Update a specific class-wise fee.
        """
        try:
            fee = ClasswiseFee.objects.get(pk=pk)
            serializer = ClasswiseFeeSerializer(fee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ClasswiseFee.DoesNotExist:
            return Response({'error': 'Classwise fee not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        Delete a specific class-wise fee.
        """
        try:
            fee = ClasswiseFee.objects.get(pk=pk)
            fee.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClasswiseFee.DoesNotExist:
            return Response({'error': 'Classwise fee not found'}, status=status.HTTP_404_NOT_FOUND)


class StudentFeeViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing student fees, accessible only to admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        """
        Retrieve a list of all student fees.
        """
        student_fees = StudentFee.objects.all()
        serializer = StudentFeeSerializer(student_fees, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new student fee record.
        """
        serializer = StudentFeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific student fee record by its ID.
        """
        try:
            student_fee = StudentFee.objects.get(pk=pk)
            serializer = StudentFeeSerializer(student_fee)
            return Response(serializer.data)
        except StudentFee.DoesNotExist:
            return Response({'error': 'Student fee record not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        Update an existing student fee record.
        """
        try:
            student_fee = StudentFee.objects.get(pk=pk)
            serializer = StudentFeeSerializer(student_fee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentFee.DoesNotExist:
            return Response({'error': 'Student fee record not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        Delete a specific student fee record.
        """
        try:
            student_fee = StudentFee.objects.get(pk=pk)
            student_fee.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except StudentFee.DoesNotExist:
            return Response({'error': 'Student fee record not found'}, status=status.HTTP_404_NOT_FOUND)

class StaffSalaryViewSet(viewsets.ViewSet):

# List Salaries: GET /api/staff-salaries/
# Create Salary: POST /api/staff-salaries/
# Retrieve Salary: GET /api/staff-salaries/<salary_id>/
# Update Salary: PUT /api/staff-salaries/<salary_id>/
# Delete Salary: DELETE /api/staff-salaries/<salary_id>/
    """
    A ViewSet for managing staff salaries, accessible only to admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        """
        Retrieve a list of all staff salaries.
        """
        staff_salaries = StaffSalary.objects.all()
        serializer = StaffSalarySerializer(staff_salaries, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new staff salary record.
        """
        serializer = StaffSalarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific staff salary record.
        """
        try:
            staff_salary = StaffSalary.objects.get(pk=pk)
            serializer = StaffSalarySerializer(staff_salary)
            return Response(serializer.data)
        except StaffSalary.DoesNotExist:
            return Response({'error': 'Staff salary record not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        Update an existing staff salary record.
        """
        try:
            staff_salary = StaffSalary.objects.get(pk=pk)
            serializer = StaffSalarySerializer(staff_salary, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StaffSalary.DoesNotExist:
            return Response({'error': 'Staff salary record not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        Delete a specific staff salary record.
        """
        try:
            staff_salary = StaffSalary.objects.get(pk=pk)
            staff_salary.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except StaffSalary.DoesNotExist:
            return Response({'error': 'Staff salary record not found'}, status=status.HTTP_404_NOT_FOUND)

#-------------------------------------------------------------------------





# class StudentEnrollmentViewSet(viewsets.ModelViewSet):
#     queryset = StudentEnrollment.objects.all()
#     serializer_class = StudentEnrollmentSerializer


class StaffEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StaffEnrollment.objects.all()
    serializer_class = StaffEnrollmentSerializer


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer


class StudentFeeViewSet(viewsets.ModelViewSet):
    queryset = StudentFee.objects.all()
    serializer_class = StudentFeeSerializer


class StaffSalaryViewSet(viewsets.ModelViewSet):
    queryset = StaffSalary.objects.all()
    serializer_class = StaffSalarySerializer


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer


class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.all()
    serializer_class = StaffAttendanceSerializer


class StudentFeedbackViewSet(viewsets.ModelViewSet):
    queryset = StudentFeedback.objects.all()
    serializer_class = StudentFeedbackSerializer


class StaffFeedbackViewSet(viewsets.ModelViewSet):
    queryset = StaffFeedback.objects.all()
    serializer_class = StaffFeedbackSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class ExtracurricularActivityViewSet(viewsets.ModelViewSet):
    queryset = ExtracurricularActivity.objects.all()
    serializer_class = ExtracurricularActivitySerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class ClassTimetableViewSet(viewsets.ModelViewSet):
    queryset = ClassTimetable.objects.all()
    serializer_class = ClassTimetableSerializer


class ExaminationTimetableViewSet(viewsets.ModelViewSet):
    queryset = ExaminationTimetable.objects.all()
    serializer_class = ExaminationTimetableSerializer


class CounselingSessionViewSet(viewsets.ModelViewSet):
    queryset = CounselingSession.objects.all()
    serializer_class = CounselingSessionSerializer


class BehaviorReportViewSet(viewsets.ModelViewSet):
    queryset = BehaviorReport.objects.all()
    serializer_class = BehaviorReportSerializer


class CertificateRequestsStudentViewSet(viewsets.ModelViewSet):
    queryset = CertificateRequestsStudent.objects.all()
    serializer_class = CertificateRequestsStudentSerializer
