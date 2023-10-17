from django.contrib import admin
from .models import VideoSeries, Video, Resource,Notification
# Register your models here.

class VideoAdmin(admin.ModelAdmin):
    list_display=[
        "videoName","fromSeires","showingAtLandingPage","showingFirstly","carouselInfo","createdAt"
    ]
admin.site.register(VideoSeries)
admin.site.register(Video,VideoAdmin)
admin.site.register(Resource)
admin.site.register(Notification)
