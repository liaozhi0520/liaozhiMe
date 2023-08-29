from django.shortcuts import render
from django.views import View
from web.models import VideoSeries,Video

class BilibiliVideoDocsView(View):
    def get(self,request,*args, **kwargs):
        docTemplateUrl=request.GET.get('docTemplateUrl',None)
        allVideoSeriesObj=VideoSeries.objects.all()
        dataRetrieved=[]
        validDocTemplateUrl=[]
        for videoSeries in allVideoSeriesObj:
            videoSeriesData={
                'videoSeriesId':videoSeries.id,
                'videoSeriesName':videoSeries.seriesName,
                'videosFromVideoSeries':[]
            }
            for video in videoSeries.video_set.all():
                videoData={
                    'videoId':video.id,
                    'videoName':video.videoName,
                }
                videoSeriesData['videosFromVideoSeries'].append(videoData)
                validDocTemplateUrl.append(f'web/bilibiliVideoDocTemplates/{videoSeries.id}/{video.id}')
            dataRetrieved.append(videoSeriesData)
        if not docTemplateUrl:
            context={
                'dataRetrieved':dataRetrieved
            }
            return render(request,'web/bilibiliVideoDocTemplates/docIndex.html',context=context)
        if docTemplateUrl in validDocTemplateUrl:
            context={
                'dataRetrieved':dataRetrieved,
                'imgUrlPrefix':'web/img/'+docTemplateUrl.split('/',1)[1]
            }
            return render(request,f'{docTemplateUrl}/doc.html',context=context)
        else:
            context={'dataRetrieved':dataRetrieved}
            return render(request,'web/bilibiliVideoDocTemplates/docNotFound.html',context=context)
        