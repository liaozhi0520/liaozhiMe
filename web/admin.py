from django.contrib import admin
from .models import Series, Article,Notification,Resource
#Register your models here.


admin.site.register(Series)
admin.site.register(Article)
admin.site.register(Resource)
admin.site.register(Notification)
