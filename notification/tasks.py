from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import requests
from .models import EmailNotification, SMSNotification, Notification


@shared_task
def send_email_task(email_id):
    """Email yuborish"""
    try:
        email = EmailNotification.objects.get(id=email_id)
    except EmailNotification.DoesNotExist:
        return f"EmailNotification {email_id} not found"

    try:
        send_mail(
            subject=email.subject,
            message=email.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email.to_email],
            fail_silently=False,
        )
        email.status = "sent"
        email.sent_at = timezone.now()
        email.save()
        return f"Email sent to {email.to_email}"
    except Exception as e:
        email.status = "failed"
        email.error_message = str(e)
        email.save()
        return f"Email failed: {str(e)}"


@shared_task
def send_pending_emails(batch_size=50):
    """Navbatdagi barcha email'larni yuborish"""
    pending_emails = EmailNotification.objects.filter(status="pending")[:batch_size]
    for email in pending_emails:
        send_email_task.delay(email.id)
    return f"Queued {pending_emails.count()} emails for sending"


@shared_task
def send_sms_task(sms_id):
    """SMS yuborish"""
    try:
        sms = SMSNotification.objects.get(id=sms_id)
    except SMSNotification.DoesNotExist:
        return f"SMSNotification {sms_id} not found"

    try:
        api_url = "https://notify.eskiz.uz/api/message/sms/send"
        headers = {"Authorization": f"Bearer {settings.ESKIZ_API_TOKEN}"}
        data = {
            "mobile_phone": sms.phone,
            "message": sms.message,
            "from": "4546",
        }

        response = requests.post(api_url, headers=headers, data=data)
        if response.status_code == 200:
            sms.status = "sent"
            sms.sent_at = timezone.now()
        else:
            sms.status = "failed"
            sms.error_message = response.text
        sms.save()
        return (
            f"SMS sent to {sms.phone}"
            if sms.status == "sent"
            else f"SMS failed to {sms.phone}"
        )
    except Exception as e:
        sms.status = "failed"
        sms.error_message = str(e)
        sms.save()
        return f"SMS failed: {str(e)}"


@shared_task
def send_pending_sms(batch_size=50):
    """Navbatdagi barcha SMS larni yuborish"""
    pending_sms = SMSNotification.objects.filter(status="pending")[:batch_size]
    for sms in pending_sms:
        send_sms_task.delay(sms.id)
    return f"Queued {pending_sms.count()} SMS for sending"


@shared_task
def create_notification(user_id, title, message, notification_type="info", link=""):
    """Tizim ichida bildirishnoma yaratish"""
    try:
        from hisoblar.models import User

        user = User.objects.get(id=user_id)
    except Exception as e:
        return f"Failed to create notification: {str(e)}"

    Notification.objects.create(
        user=user, title=title, message=message, type=notification_type, link=link
    )
    return f"Notification created for {user.name}"


@shared_task
def send_payment_reminder(student_id):
    """To'lov eslatmasi yuborish"""
    try:
        from akademk.models import Student
        from moliya.models import Debt

        student = Student.objects.get(id=student_id)
        debts = Debt.objects.filter(student=student, status="pending")
        if not debts.exists():
            return f"No pending debts for {student.user.name}"

        total_debt = sum(debt.amount for debt in debts)

        # Tizim ichidagi bildirishnoma
        create_notification.delay(
            user_id=student.user.id,
            title="To'lov eslatmasi",
            message=f"Sizning {total_debt:,.0f} so'm qarzdorligingiz bor.",
            notification_type="warning",
            link="/payments",
        )

        # SMS
        sms = SMSNotification.objects.create(
            phone=student.user.phone,
            message=f"Hurmatli {student.user.name}, sizning {total_debt:,.0f} so'm qarzdorligingiz bor. Iltimos to'lovni amalga oshiring.",
        )
        send_sms_task.delay(sms.id)

        # Email
        email = EmailNotification.objects.create(
            to_email=student.user.email,
            subject="To'lov eslatmasi",
            body=f"Hurmatli {student.user.name},\n\nSizning {total_debt:,.0f} so'm qarzdorligingiz bor.\n\nIltimos to'lovni amalga oshiring.",
        )
        send_email_task.delay(email.id)

        return f"Reminder queued for {student.user.name}"

    except Exception as e:
        return f"Failed to send reminder: {str(e)}"


@shared_task
def send_bulk_notification(user_ids, title, message):
    """Ko'p foydalanuvchilarga bildirishnoma yuborish"""
    for user_id in user_ids:
        create_notification.delay(user_id, title, message)
    return f"Queued notifications for {len(user_ids)} users"
