from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils import translation
from django.utils.translation import gettext as _
from web.models import Video
import json

class LandingPageView(View):
    def get(self,request,*args,**kwargs):
        '''
            carouselInfo structure
            carouselInfo={
                "coverImgSrc":coverImgSrc,
                "docHref":docHref,
                "coverCaptionSeriesName":coverCaptionSeriesName,
                "coverCaptionVideoName":coverCaptionVideoName
            }
        '''
        recommendedVideos=Video.objects.filter(showingAtLandingPage=True).all()    
        carouselsInfo=[]
        for vid in recommendedVideos:
                infoJson=vid.carouselInfo
                carouselInfo=json.loads(infoJson)
                if vid.showingFirstly:
                    carouselsInfo.insert(0,carouselInfo)
                else:
                    carouselsInfo.append(carouselInfo)
        context={
            "carouselsInfo":carouselsInfo
        }
        return render(request,'web/landingpage.html',context)

class ChangeLanguageView(View):
    def get(self,request,*args,**kwargs):
        languageCode=request.GET.get('languageCode')
        if languageCode not in ['zh','en']:
            response={
                'flag':False,
                'message':_('Sorry, it seems like you did not pass the correct language code to server.')
            }
            return JsonResponse(response)
        else:
            translation.activate(languageCode)
            request.session[translation.LANGUAGE_SESSION_KEY]=languageCode
            response={
                'flag':True
            }
            return JsonResponse(response)

class CloseNotificationView(View):
    def get(self,request,*args,**kwargs):
        readNotificationId=request.GET.get('readNotificationId')
        try:
            request.session['readNotificationId'] = readNotificationId
            response = {
                'flag':True
            }
            return JsonResponse(response)
        except Exception as e:
            response={
                'flag':False,
                'message':_('Sorry, the server may glitched. This is the error messeage from server: ')+str(e)
            }
            return JsonResponse(response)