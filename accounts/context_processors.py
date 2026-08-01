from .models import Notification

def notification_context(request):

    if not request.user.is_authenticated:
        return {}

    notifications = Notification.objects.filter(
        receiver=request.user,
        is_resolved=False,
    ).order_by("-created_at")

    unread_count = notifications.filter(
        is_read=False,
    ).count()

    return {
        "notifications": notifications,
        "unread_notification_count": unread_count,
    }