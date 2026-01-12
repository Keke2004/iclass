from django.urls import path
from .views import NotificationViewSet

notification_list = NotificationViewSet.as_view({
    'get': 'list'
})

notification_mark_all_as_read = NotificationViewSet.as_view({
    'post': 'mark_all_as_read'
})

notification_unread_count = NotificationViewSet.as_view({
    'get': 'unread_count'
})

notification_mark_as_read = NotificationViewSet.as_view({
    'post': 'mark_as_read'
})

urlpatterns = [
    path('notifications/', notification_list, name='notification-list'),
    path('notifications/mark_all_as_read/', notification_mark_all_as_read, name='notification-mark-all-as-read'),
    path('notifications/unread_count/', notification_unread_count, name='notification-unread-count'),
    path('notifications/<int:pk>/mark_as_read/', notification_mark_as_read, name='notification-mark-as-read'),
]
