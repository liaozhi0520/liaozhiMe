from django.shortcuts import render
from django.views import View
from web.models import Series,Article
import re

class DocsView(View):
    def get(self,request,*args, **kwargs):
        docTemplateUrl=request.GET.get('docTemplateUrl',None)
        requestingSeriesEnName=docTemplateUrl.split("/")[0] if ((docTemplateUrl is not None) and bool(re.search(r"\w+/\w+",docTemplateUrl)) )else None
        requestingArticleEnName=docTemplateUrl.split("/")[1] if ((docTemplateUrl is not None) and bool(re.search(r"\w+/\w+",docTemplateUrl))) else None
        allSeriesObj=Series.objects.all()
        dataRetrieved=[]
        validDocTemplateUrl=[]
        for series in allSeriesObj:     
            seriesData={
                'id':series.id,
                "enName":series.enName,
                'name':series.name,
                'articlesFromThisSeries':[],
                "requested":True if series.enName==requestingSeriesEnName else False
            }
            for article in series.article_set.all():
                articleData={
                    'id':article.id,
                    "enName":article.enName,
                    'name':article.name,
                    "requested":True if article.enName==requestingArticleEnName else False   
                }
                seriesData['articlesFromThisSeries'].append(articleData)
                validDocTemplateUrl.append("/".join([series.enName,article.enName]))
            dataRetrieved.append(seriesData)
        if not docTemplateUrl:
            context={
                'dataRetrieved':dataRetrieved
            }
            return render(request,'web/docTemplates/docIndex.html',context=context)
        if docTemplateUrl in validDocTemplateUrl:
            context={
                'dataRetrieved':dataRetrieved,
            }
            return render(request,"/".join(["web","docTemplates",docTemplateUrl,"doc.html"]),context=context)
        else:
            context={'dataRetrieved':dataRetrieved}
            return render(request,'web/docTemplates/docNotFound.html',context=context)
        