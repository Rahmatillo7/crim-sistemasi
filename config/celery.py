import os
from celery import Celery
from celery.schedules import crontab

# Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Celery app yaratish
app = Celery("manbacrm")  # 'config' o'rniga loyiha nomi

# Django settings'dan konfiguratsiya
app.config_from_object("django.conf:settings", namespace="CELERY")

# Barcha app'lardagi tasks.py fayllarini avtomatik topish
app.autodiscover_tasks()

# Periodik vazifalar (Celery Beat)
app.conf.beat_schedule = {
    # Test task - har minutda
    "test-task-every-minute": {
        "task": "notification.tasks.send_pending_sms",
        "schedule": crontab(),  # Har minutda (default)
        # Yoki: 'schedule': 60.0,  # 60 sekund
    },
    # Qarzlarni tekshirish - har minutda
    "check-debts-every-minute": {
        "task": "moliya.tasks.check_overdue_debts",
        "schedule": crontab(),  # Har minutda
    },
    # To'lov eslatmasi - har minutda
    "payment-reminder-every-minute": {
        "task": "moliya.tasks.send_payment_reminder_before_due",
        "schedule": crontab(),  # Har minutda
        "kwargs": {"days_before": 3},
    },
    # Davomat tekshiruvi - har minutda
    "check-attendance-every-minute": {
        "task": "akademk.tasks.check_low_attendance",
        "schedule": crontab(),  # Har minutda
    },
    # SMS yuborish - har minutda
    "send-pending-sms-every-minute": {
        "task": "notification.tasks.send_pending_sms",
        "schedule": 60.0,  # 60 sekund = 1 minut
    },
    # Email yuborish - har minutda
    "send-pending-emails-every-minute": {
        "task": "notification.tasks.send_pending_emails",
        "schedule": 60.0,  # 60 sekund = 1 minut
    },
    # ======== PRODUCTION UCHUN (keyinroq o'zgartiring) ========
    # Qarzlarni tekshirish - har kuni soat 9:00 (ishlatilmayapti)
    # 'check-debts-daily': {
    #     'task': 'moliya.tasks.check_overdue_debts',
    #     'schedule': crontab(hour=9, minute=0),
    # },
    # To'lov eslatmasi - har kuni soat 10:00 (ishlatilmayapti)
    # 'payment-reminder-3days': {
    #     'task': 'moliya.tasks.send_payment_reminder_before_due',
    #     'schedule': crontab(hour=10, minute=0),
    #     'kwargs': {'days_before': 3}
    # },
    # Davomat tekshiruvi - har dushanba soat 10:00 (ishlatilmayapti)
    # 'check-attendance-weekly': {
    #     'task': 'akademk.tasks.check_low_attendance',
    #     'schedule': crontab(day_of_week=1, hour=10, minute=0),
    # },
    # SMS yuborish - har 30 daqiqada (ishlatilmayapti)
    # 'send-pending-sms': {
    #     'task': 'notification.tasks.send_pending_sms',
    #     'schedule': 1800.0,  # 30 daqiqa
    # },
}

# Timezone
app.conf.timezone = "Asia/Tashkent"


# Debug task
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
