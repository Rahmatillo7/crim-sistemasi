from django.contrib import admin
from .models import Notification, EmailNotification, SMSNotification, PushNotification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["user__name", "user__email", "title", "message"]
    readonly_fields = ["created_at"]


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ["to_email", "subject", "status", "created_at", "sent_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["to_email", "subject"]
    readonly_fields = ["created_at", "sent_at"]


@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
    list_display = ["phone", "message", "status", "provider", "created_at", "sent_at"]
    list_filter = ["status", "provider", "created_at"]
    search_fields = ["phone", "message"]
    readonly_fields = ["created_at", "sent_at"]


@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "status", "created_at", "sent_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__name", "title", "body"]
    readonly_fields = ["created_at", "sent_at"]
