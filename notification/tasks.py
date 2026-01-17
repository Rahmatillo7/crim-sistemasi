from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import requests

from akademk.models import Student
from moliya.models import Debt
from .models import EmailNotification, SMSNotification, Notification


# ----------------- SMS/Email tasks -----------------
@shared_task
def send_sms_task(sms_id):
    try:
        sms = SMSNotification.objects.get(id=sms_id)
    except SMSNotification.DoesNotExist:
        return f"SMSNotification {sms_id} not found"

    try:
        api_url = "https://notify.eskiz.uz/api/message/sms/send"
        headers = {"Authorization": f"Bearer {settings.ESKIZ_API_TOKEN}"}
        data = {"mobile_phone": sms.phone, "message": sms.message, "from": "4546"}
        response = requests.post(api_url, headers=headers, data=data)
        if response.status_code == 200:
            sms.status = "sent"
            sms.sent_at = timezone.now()
        else:
            sms.status = "failed"
            sms.error_message = response.text
        sms.save()
        return f"SMS {'sent' if sms.status=='sent' else 'failed'} to {sms.phone}"
    except Exception as e:
        sms.status = "failed"
        sms.error_message = str(e)
        sms.save()
        return f"SMS failed: {str(e)}"


@shared_task
def send_pending_sms(batch_size=50):
    pending_sms = SMSNotification.objects.filter(status="pending")[:batch_size]
    for sms in pending_sms:
        send_sms_task.delay(sms.id)
    return f"Queued {pending_sms.count()} SMS for sending"


@shared_task
def send_email_task(email_id):
    try:
        email = EmailNotification.objects.get(id=email_id)
    except EmailNotification.DoesNotExist:
        return f"EmailNotification {email_id} not found"

    try:
        send_mail(
            subject=email.subject,
            message=email.message,
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
    pending_emails = EmailNotification.objects.filter(status="pending")[:batch_size]
    for email in pending_emails:
        send_email_task.delay(email.id)
    return f"Queued {pending_emails.count()} emails for sending"


# ----------------- Payment reminder -----------------
@shared_task(bind=True)
def send_payment_reminder_before_due(self, days_before=3):
    """Payment reminder task for Beat"""
    from akademk.models import Student
    from moliya.models import Debt
    from django.utils import timezone

    target_date = timezone.now() + timezone.timedelta(days=days_before)

    for student in Student.objects.all():
        debts = Debt.objects.filter(student=student, status="pending")
        if debts.exists():
            total_debt = sum(d.amount for d in debts)
            # Notification
            Notification.objects.create(
                user=student.user,
                title="To'lov eslatmasi",
                message=f"Sizning {total_debt:,.0f} so'm qarzdorligingiz bor.",
                type="warning",
                link="/payments",
            )
            # SMS
            sms = SMSNotification.objects.create(
                phone=student.user.phone,
                message=f"Hurmatli {student.user.name}, sizning {total_debt:,.0f} so'm qarzdorligingiz bor. Iltimos to'lovni amalga oshiring.",
                status="pending",
            )
            send_sms_task.delay(sms.id)
            # Email
            email = EmailNotification.objects.create(
                to_email=student.user.email,
                subject="To'lov eslatmasi",
                message=f"Hurmatli {student.user.name}, sizning {total_debt:,.0f} so'm qarzdorligingiz bor.\n\nIltimos to'lovni amalga oshiring.",
                status="pending",
            )
            send_email_task.delay(email.id)

    return "Payment reminders queued"
