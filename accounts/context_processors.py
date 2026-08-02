from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(receiver=request.user).order_by("-created_at")[:10]
        unread_count = Notification.objects.filter(receiver=request.user, is_read=False).count()
        return {
            "notifications": user_notifications,
            "unread_notification_count": unread_count,
        }
    return {
        "notifications": [],
        "unread_notification_count": 0,
    }