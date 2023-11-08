from django.conf.urls import re_path
from .views.landingpage import LandingPageView,ChangeLanguageView,CloseNotificationView
from .views.resources import ResourceDownloadView
from .views.docs import DocsView




urlpatterns=[
    re_path('^$',LandingPageView.as_view(),name='landingpage'),
    re_path('^resourcesDownload$',ResourceDownloadView.as_view(),name='resourcesDownload'),
    re_path('^changeLanguage$',ChangeLanguageView.as_view(),name='changeLanguage'),
    re_path('^closeNotification$',CloseNotificationView.as_view(),name='closeNotification'),
    re_path('^docs$',DocsView.as_view(),name='docs')
]