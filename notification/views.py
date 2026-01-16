from rest_framework import viewsets
from notification.models import (
    Notification,
    EmailNotification,
    SMSNotification,
    PushNotification,
)
from notification.serializers import (
    NotificationSerializer,
    EmailNotificationSerializer,
    SMSNotificationSerializer,
    PushNotificationSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class EmailNotificationViewSet(viewsets.ModelViewSet):
    queryset = EmailNotification.objects.all()
    serializer_class = EmailNotificationSerializer


class SMSNotificationViewSet(viewsets.ModelViewSet):
    queryset = SMSNotification.objects.all()
    serializer_class = SMSNotificationSerializer


class PushNotificationViewSet(viewsets.ModelViewSet):
    queryset = PushNotification.objects.all()
    serializer_class = PushNotificationSerializer
