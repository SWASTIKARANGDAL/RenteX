from apps.products.models import Category


def global_context(request):
    ctx = {
        'categories': Category.objects.all().order_by('order', 'name'),
    }
    if request.user.is_authenticated:
        from apps.notifications.models import Notification
        ctx['unread_notifications_count'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    return ctx
