from django.conf.urls import re_path
from .views.landingpage import LandingPageView,ChangeLanguageView,CloseNotificationView
from .views.bilibiliVidResourceDl import DownloadPageView



urlpatterns=[
    re_path('^$',LandingPageView.as_view(),name='landingpage'),
    re_path('^bilibiliResourceDownload$',DownloadPageView.as_view(),name='bilibiliResourceDownload'),
    re_path('^changeLanguage$',ChangeLanguageView.as_view(),name='changeLanguage'),
    re_path(r'^closeNotification$',CloseNotificationView.as_view(),name='closeNotification')
]