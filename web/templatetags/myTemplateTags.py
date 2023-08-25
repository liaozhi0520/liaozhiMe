from django import template
from web.models import Notification
register=template.Library()


@register.inclusion_tag(r'web/templateTagsHtml/notification.html')
def notification(request):
    readNotificationId=request.session.get('readNotificationId',0)
    latestNotification=Notification.objects.order_by('id').last()
    if  latestNotification and int(latestNotification.id)>int(readNotificationId):
        needToShowNotification=True
        notificationData={
            'notificationId':latestNotification.id,
            'notifitionImgSrc':r'web/img/normalNotification.svg' if latestNotification.type=='normal' else r'web/img/dangerNotification.svg',
            'notificationText':latestNotification.text,
            'notificationCreatedTime':latestNotification.createdAt.strftime('%Y-%m-%d %H:%M')
        }
        context={
            'needToShowNotification':needToShowNotification,
            'notificationData':notificationData
        }
        return context
    else:
        context={
            'needToShowNotification':False
        }
        return context