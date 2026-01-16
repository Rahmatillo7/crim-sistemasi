from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Importlar
from akademk.viewa import (
    CourseViewSet,
    GroupViewSet,
    ScheduleViewSet,
    StudentViewSet,
    EnrollmentViewSet,
)
from hisoblar.viewa import AuthViewSet, UserViewSet, RoleViewSet
from ishtirok.viewa import (
    AttendanceViewSet,
    HomeworkViewSet,
    HomeworkSubmissionViewSet,
    ScoreViewSet,
    CenterAnalyticsViewSet,
)
from moliya.viewa import PaymentViewSet, DebtViewSet
from notification.views import (
    EmailNotificationViewSet,
    SMSNotificationViewSet,
    PushNotificationViewSet,
    NotificationViewSet,
)
from potential.viewa import LeadViewSet
from yadro.viewa import CenterViewSet, BranchViewSet, RoomViewSet, ActivityLogViewSet

# Faqat bitta router
router = DefaultRouter()

# Authentication & Users
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="users")
router.register(r"roles", RoleViewSet, basename="roles")

# Core
router.register(r"centers", CenterViewSet, basename="center")
router.register(r"branches", BranchViewSet, basename="branch")
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"activity-logs", ActivityLogViewSet, basename="activity-log")

# Academic
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"schedules", ScheduleViewSet, basename="schedule")
router.register(r"students", StudentViewSet, basename="student")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

# Notifications
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(
    r"email-notifications", EmailNotificationViewSet, basename="emailnotification"
)
router.register(
    r"sms-notifications", SMSNotificationViewSet, basename="smsnotification"
)
router.register(
    r"push-notifications", PushNotificationViewSet, basename="pushnotification"
)

# Attendance & LMS
router.register(r"attendance", AttendanceViewSet, basename="attendance")
router.register(
    r"center-analytics", CenterAnalyticsViewSet, basename="center-analytics"
)
router.register(r"homeworks", HomeworkViewSet, basename="homework")
router.register(
    r"homework-submissions", HomeworkSubmissionViewSet, basename="homework-submission"
)
router.register(r"scores", ScoreViewSet, basename="score")

# Finance
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"debts", DebtViewSet, basename="debt")

# Leads
router.register(r"leads", LeadViewSet, basename="lead")

# URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# Static & media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
