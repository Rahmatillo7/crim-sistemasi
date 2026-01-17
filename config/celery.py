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
from celery.schedules import crontab

app.conf.beat_schedule = {
    "send-pending-sms-every-minute": {
        "task": "notification.tasks.send_pending_sms",
        "schedule": 60.0,  # har minut
    },
    "send-pending-emails-every-minute": {
        "task": "notification.tasks.send_pending_emails",
        "schedule": 60.0,
    },
    "check-low-attendance-every-minute": {
        "task": "akademk.tasks.check_low_attendance",
        "schedule": crontab(),
    },
    "payment-reminder-every-minute": {
        "task": "moliya.tasks.send_payment_reminder_before_due",
        "schedule": crontab(),
    },
    "test-class-reminder-every-minute": {
        "task": "akademk.tasks.send_class_reminder",
        "schedule": crontab(),
    },
}

app.conf.timezone = "Asia/Tashkent"


# Debug task
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
