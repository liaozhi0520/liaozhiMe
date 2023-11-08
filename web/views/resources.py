from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from web.models import Series,Article,Resource

class ResourceDownloadView(View):
    def get(self,request,*args,**kwargs):
        dataRetrieved = []
        allSeries=Series.objects.all()
        for series in allSeries:
            seriesData={
                'id': series.id,
                'name': series.name,
                'articlesFromThisSeries':[]
            }
            articlesFromThisSeries=series.article_set.all()
            for article in articlesFromThisSeries:
                articleData={
                    'id':article.id,
                    'name':article.name,
                    'resourcesFromThisArticle':[]
                }
                resourcesFromThisArticle=article.resource_set.all()
                for resource in resourcesFromThisArticle:
                    resourceData={
                        'id':resource.id,
                        'downloadUrl':resource.downloadUrl,
                        'name':resource.name
                    }
                    articleData['resourcesFromThisArticle'].append(resourceData)
                seriesData['articlesFromThisSeries'].append(articleData)
            dataRetrieved.append(seriesData)
        context={
            'dataRetrieved':dataRetrieved,
        }
        return render(request,'web/resourceDl.html',context)

