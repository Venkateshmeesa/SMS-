from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'admin-registration', AdminPrincipalRegistrationView, basename='admin-registration')
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'classes/(?P<class_pk>[^/.]+)/students', ClassStudentsViewSet, basename='class-students')
router.register(r'classes/(?P<class_id>[^/.]+)/subjects', SubjectViewSet, basename='class-subjects')
# router.register(r'students', StudentEnrollmentViewSet)
router.register(r'staff', StaffEnrollmentViewSet)
router.register(r'student-profiles', StudentProfileViewSet)
router.register(r'staff-profiles', StaffProfileViewSet)
router.register(r'staff-enrollments', StaffEnrollmentViewSet, basename='staff-enrollment')
router.register(r'student-enrollments', StudentEnrollmentViewSet, basename='student-enrollment')
router.register(r'subjects', SubjectViewSet)
router.register(r'parents', ParentViewSet)
router.register(r'student-fees', StudentFeeViewSet)
router.register(r'staff-salaries', StaffSalaryViewSet)
router.register(r'student-attendance', StudentAttendanceViewSet)
router.register(r'staff-attendance', StaffAttendanceViewSet)
router.register(r'student-feedback', StudentFeedbackViewSet)
router.register(r'staff-feedback', StaffFeedbackViewSet)
router.register(r'events', EventViewSet)
router.register(r'extracurricular-activities', ExtracurricularActivityViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'class-timetables', ClassTimetableViewSet)
router.register(r'examination-timetables', ExaminationTimetableViewSet)
router.register(r'counseling-sessions', CounselingSessionViewSet)
router.register(r'behavior-reports', BehaviorReportViewSet)
router.register(r'certificate-requests', CertificateRequestsStudentViewSet)
router.register(r'student-fees', StudentFeeViewSet, basename='student-fee')
router.register(r'classwise-fees', ClasswiseFeeViewSet, basename='classwisefee')
router.register(r'staff-salaries', StaffSalaryViewSet, basename='staff-salary')




urlpatterns = [
    
    path('login-admin/', AdminLoginView.as_view(), name='login-admin'),
    path('api/classes/<int:class_id>/subjects/<int:pk>/', SubjectViewSet.as_view({'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'destroy'}), name='class-subjects'),
    path('', include(router.urls)),  # Include all router URLsworkon data12
]
urlpatterns += router.urls