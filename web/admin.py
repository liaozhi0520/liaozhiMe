from django.contrib import admin
from .models import VideoSeries, Video, Resource,Notification
# Register your models here.
admin.site.register(VideoSeries)
admin.site.register(Video)
admin.site.register(Resource)
admin.site.register(Notification)
