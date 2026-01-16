from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from notification.models import Notification, SMSNotification
from akademk.models import Group, Enrollment, Student, Schedule
from ishtirok.models import Homework, HomeworkSubmission, Attendance
from yadro.models import Center
from moliya.models import Payment


@shared_task
def send_class_reminder(group_id, hours_before=2):
    """Dars boshlanishidan oldin eslatma yuborish"""
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return f"Group {group_id} not found"

    today = timezone.now().date()
    current_weekday = today.weekday()

    schedules = Schedule.objects.filter(group=group, day_of_week=str(current_weekday))
    if not schedules.exists():
        return "No classes today"

    enrollments = Enrollment.objects.filter(group=group, status="active")
    for enrollment in enrollments:
        for schedule in schedules:
            Notification.objects.create(
                user=enrollment.student.user,
                title="Dars eslatmasi",
                message=f"{hours_before} soatdan keyin {group.name} darsi boshlanadi. Vaqti: {schedule.start_time.strftime('%H:%M')}",
                type="info",
                link=f"/groups/{group.id}",
            )
            if enrollment.student.user.phone:
                SMSNotification.objects.create(
                    phone=enrollment.student.user.phone,
                    message=f"Eslatma: {hours_before} soatdan keyin {group.name} darsi. Vaqt: {schedule.start_time.strftime('%H:%M')}",
                )

    return f"Reminders sent to {enrollments.count()} students"


@shared_task
def send_homework_deadline_reminder(homework_id):
    """Vazifa muddati tugashidan oldin eslatma"""
    try:
        homework = Homework.objects.get(id=homework_id)
    except Homework.DoesNotExist:
        return f"Homework {homework_id} not found"

    group = homework.group
    enrollments = Enrollment.objects.filter(group=group, status="active")
    submitted_students = HomeworkSubmission.objects.filter(
        homework=homework
    ).values_list("student_id", flat=True)
    not_submitted = enrollments.exclude(student_id__in=submitted_students)

    for enrollment in not_submitted:
        Notification.objects.create(
            user=enrollment.student.user,
            title="Vazifa eslatmasi",
            message=f"'{homework.title}' vazifasi muddati {homework.due_date.strftime('%d.%m.%Y')} kuni tugaydi!",
            type="warning",
            link=f"/homeworks/{homework.id}",
        )
        if enrollment.student.user.phone:
            SMSNotification.objects.create(
                phone=enrollment.student.user.phone,
                message=f"Vazifa '{homework.title}' muddati {homework.due_date.strftime('%d.%m.%Y')} tugaydi. Topshirishni unutmang!",
            )

    return f"Reminders sent to {not_submitted.count()} students"


@shared_task
def check_low_attendance():
    """Past davomat ko'rsatkichlari uchun ogohlantirish"""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    enrollments = Enrollment.objects.filter(status="active")

    for enrollment in enrollments:
        attendances = Attendance.objects.filter(
            student=enrollment.student,
            group=enrollment.group,
            lesson_date__gte=thirty_days_ago,
        )
        total_classes = attendances.count()
        if total_classes == 0:
            continue

        attended = attendances.filter(status="present").count()
        attendance_rate = (attended / total_classes) * 100

        if attendance_rate < 70:
            Notification.objects.create(
                user=enrollment.student.user,
                title="Past davomat!",
                message=f"{enrollment.group.name} guruhida davomatingiz {attendance_rate:.1f}%. Iltimos darsga muntazam qatnang!",
                type="error",
                link="/attendance",
            )
            if getattr(enrollment.student, "parent_phone", None):
                SMSNotification.objects.create(
                    phone=enrollment.student.parent_phone,
                    message=f"DIQQAT! {enrollment.student.user.name}ning {enrollment.group.name} guruhida davomat {attendance_rate:.1f}% ga tushdi.",
                )

    return "Low attendance check completed"


@shared_task
def generate_monthly_report(center_id):
    """Oylik hisobot yaratish"""
    try:
        center = Center.objects.get(id=center_id)
    except Center.DoesNotExist:
        return f"Center {center_id} not found"

    today = timezone.now()
    month_start = today.replace(day=1)
    total_students = Student.objects.filter(user__center=center).count()
    monthly_payments = Payment.objects.filter(
        student__user__center=center,
        created_at__gte=month_start,
        status="completed",
    )
    total_revenue = sum(p.amount for p in monthly_payments)

    report_data = {
        "center": center.name,
        "month": today.strftime("%B %Y"),
        "total_students": total_students,
        "total_revenue": float(total_revenue),
        "total_payments": monthly_payments.count(),
    }

    directors = center.users.filter(role="director")
    for director in directors:
        Notification.objects.create(
            user=director,
            title="Oylik hisobot tayyor",
            message=f"{today.strftime('%B')} oyi uchun hisobot tayyor. Umumiy daromad: {total_revenue:,.0f} so'm",
            type="success",
            link="/reports",
        )

    return f"Report generated for {center.name}"
