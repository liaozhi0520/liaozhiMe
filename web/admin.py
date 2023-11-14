from django.contrib import admin
from .models import Series, Article,Notification, SpamCheckResUserFeedback, ArticleViewCount
#Register your models here.


admin.site.register(Series)
admin.site.register(Article)
admin.site.register(Notification)
admin.site.register(SpamCheckResUserFeedback)
admin.site.register(ArticleViewCount)
