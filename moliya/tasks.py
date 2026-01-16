from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from akademk.models import Enrollment
from django.core.mail import send_mail
from notification.models import Notification, SMSNotification, EmailNotification
from .models import Payment, Debt


@shared_task
def process_payment_notification(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        student = payment.student

        Notification.objects.create(
            user=student.user,
            title="To'lov qabul qilindi",
            message=f"{payment.amount:,.0f} so'm to'lovingiz muvaffaqiyatli qabul qilindi.",
            type="success",
            link="/payments",
        )

        SMSNotification.objects.create(
            phone=student.user.phone,
            message=f"Hurmatli {student.user.name}, {payment.amount:,.0f} so'm to'lovingiz qabul qilindi. Rahmat!",
        )

        EmailNotification.objects.create(
            to_email=student.user.email,
            subject="To'lov tasdiqlanди",
            body=f"""
            Hurmatli {student.user.name},

            {payment.amount:,.0f} so'm to'lovingiz muvaffaqiyatli qabul qilindi.
            To'lov usuli: {payment.get_method_display()}
            Sana: {payment.created_at.strftime('%d.%m.%Y %H:%M')}

            Rahmat!
            """,
        )

        return f"Payment notification sent for payment #{payment.id}"

    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def check_overdue_debts():
    today = timezone.now().date()
    overdue_debts = Debt.objects.filter(status="pending", due_date__lt=today)

    count = 0
    for debt in overdue_debts:
        debt.status = "overdue"
        debt.save()

        Notification.objects.create(
            user=debt.student.user,
            title="Qarzdorlik eslatmasi",
            message=f"Sizning {debt.amount:,.0f} so'm qarzdorligingiz muddati o'tgan.",
            type="error",
            link="/debts",
        )

        SMSNotification.objects.create(
            phone=debt.student.user.phone,
            message=f"DIQQAT! {debt.amount:,.0f} so'm qarzdorligingiz muddati o'tgan. Iltimos tezroq to'lang.",
        )

        count += 1

    return f"Checked {count} overdue debts"


@shared_task
def send_payment_reminder_before_due(days_before=3):
    target_date = timezone.now().date() + timedelta(days=days_before)
    upcoming_debts = Debt.objects.filter(status="pending", due_date=target_date)

    for debt in upcoming_debts:
        Notification.objects.create(
            user=debt.student.user,
            title="To'lov eslatmasi",
            message=f"{days_before} kundan keyin {debt.amount:,.0f} so'm to'lovingiz muddati tugaydi.",
            type="warning",
            link="/debts",
        )

        SMSNotification.objects.create(
            phone=debt.student.user.phone,
            message=f"Eslatma: {days_before} kundan keyin {debt.amount:,.0f} so'm to'lov muddati tugaydi.",
        )

    return f"Sent reminders for {upcoming_debts.count()} debts"


@shared_task
def send_payment_reminder_before_due():

    now = timezone.now()

    due_soon = Enrollment.objects.filter(
        due_date__date=now.date() + timezone.timedelta(days=1), is_paid=False
    )

    for enrollment in due_soon:
        user_email = enrollment.student.user.email
        send_mail(
            subject="Payment Reminder",
            message=f"Hello {enrollment.student.user.first_name}, your payment is due tomorrow!",
            from_email="noreply@example.com",
            recipient_list=[user_email],
            fail_silently=True,
        )

    print(f"{due_soon.count()} payment reminders sent!")
