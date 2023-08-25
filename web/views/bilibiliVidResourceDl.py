from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from web.models import VideoSeries,Video,Resource

class DownloadPageView(View):
    def get(self,request,*args,**kwargs):
        dataRetrieved = []
        videoSeries=VideoSeries.objects.all()
        for series in videoSeries:
            seriesData={
                'seriesId': series.id,
                'seriesName': series.seriesName,
                'videoFromSeries':[]
            }
            videoFromSeries=series.video_set.all()
            for video in videoFromSeries:
                videoData={
                    'videoId':video.id,
                    'videoName':video.videoName,
                    'resourceFromVideo':[]
                }
                resourceFromVideo=video.resource_set.all()
                for resource in resourceFromVideo:
                    resourceData={
                        'resourceId':resource.id,
                        'resourceUrl':resource.resourceUrl,
                        'resourceName':resource.resourceName
                    }
                    videoData['resourceFromVideo'].append(resourceData)
                seriesData['videoFromSeries'].append(videoData)
            dataRetrieved.append(seriesData)
        context={
            'dataRetrieved':dataRetrieved,
        }
        return render(request,'web/bilibiliVidResourceDl.html',context)

