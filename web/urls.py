from django.conf.urls import re_path
from .views.landingpage import LandingPageView,ChangeLanguageView,CloseNotificationView
from .views.docs import DocsView
from .views.docApis.nbSpamFilter import SpamCheckView,SpamFilterResUserFeedbackView




urlpatterns=[
    re_path('^$',LandingPageView.as_view(),name='landingpage'),
    re_path('^changeLanguage$',ChangeLanguageView.as_view(),name='changeLanguage'),
    re_path('^closeNotification$',CloseNotificationView.as_view(),name='closeNotification'),
    re_path('^docs$',DocsView.as_view(),name='docs'),
    re_path("^docApis/nbSpamFilter/spamFilterCheck$",SpamCheckView.as_view(),name="spamFilterCheck"),
    re_path("^docApis/nbSpamFilter/spamFilterResUserFeedback",SpamFilterResUserFeedbackView.as_view(),name="spamFilterResUserFeedback")
]