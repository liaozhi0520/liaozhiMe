import os
import sys
import django
baseDir=os.path.dirname(__file__)
## django env setup
sys.path.append(baseDir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','liaozhiMe.settings')
django.setup()

import argparse
import re,shutil
from bs4 import BeautifulSoup
from urllib.parse import quote,unquote
import uuid
import copy
from web.models import Series,Article,ArticleViewCount
from django.shortcuts import resolve_url
import json
from datetime import datetime


def validateTutNo(value):
    if not re.match(r".*/.*"):
        raise argparse.ArgumentTypeError("You should input the tuturial No like the format of videoSeriesId/videoId ")
    return value
def copyFilesRecursively(srcDir,destinationDir):
    for fileName in os.listdir(srcDir):
        filePath=os.path.join(srcDir,fileName)
        if os.path.isdir(filePath):
            desDirPath=os.path.join(destinationDir,fileName)
            if not os.path.exists(desDirPath):
                os.mkdir(desDirPath)
            copyFilesRecursively(filePath,desDirPath)
        else:
            newFilePath=os.path.join(destinationDir,fileName)
            shutil.copy(filePath,newFilePath)
def findSpecifiedScrAttr(tag):
        if (tag.has_attr("href") and tag['href'].startswith(quote(assetsDirName))) or (tag.has_attr("src") and tag['src'].startswith(quote(assetsDirName))):
            return True
        else:
            return False
def excludeTableOfContentsLink(tag):
        filterRes=None
        if tag.name!='a':
            filterRes=False
            return filterRes
        else:
            if "table_of_contents-link" in tag.get("class",[]):
                filterRes=False
                return filterRes
            else:
                return True

def validateImgWithAnchor(tag):
    if tag.name=="a" and tag.find("img"):
        return True
    else:
        return False

def createNewSeries():
    enName=input("input the english name of series: ").strip()
    name=input("input the Chinese name of series: ").strip()
    try:
        series=Series.objects.create(enName=enName,name=name)
        creatingRes=(True,series)
    except Exception as e:
        creatingRes=(False,str(e))
    return creatingRes

def createNewArticle(seriesId):
    enName=input("input the enName of new article: ")
    name=input("input the name of article: ")
    try:
        article=Article.objects.create(enName=enName,name=name,fromSeries_id=seriesId,carouselInfo="None")
        creatingRes=(True,article)
    except Exception as e:
        creatingRes=(False,str(e))
    return creatingRes

parser=argparse.ArgumentParser(description="This is a python script for converting the exported notion html to my own blog html")
parser.add_argument("-p","--propDir", type=str, required=True, help="Input path of the dir including the exported notion html.")
parser.add_argument("-b","--bilibiliVidHref",required=False, default="#",type=str,help="If you got a bilibili video for this tutorial, then you can input one, otherwise it is set to #")
args=parser.parse_args()
checkInput=input(f"This is the arguments you input, please check it again:\n--propDir:{args.propDir}\n--bilibiliVidHref:{args.bilibiliVidHref}\ntpye [y|n] to proceed:\n").strip().lower()
while True:
    if not re.match(r"y|n",checkInput):
        checkInput=input(f"Please input y or n").strip().lower()
    else:
        break
if checkInput=="y":
    # retrieve the series data and prompt user to input the series id where this article being placed
    allSeries=Series.objects.all()
    seriesToLandArticle=None
    promptStr=""
    if not allSeries:
        promptStr="There is no series now.Please create a new one."
        creatingFlag,seriesToLandArticle=createNewSeries()
        if not creatingFlag:
            print(seriesToLandArticle)
            sys.exit(0)
    else:
        indexes=[]
        for index,series in enumerate(allSeries):
            indexes.append(str(index))
            promptStr=promptStr+f"series-index-[{index}]:{series.name}\n"
        promptStr=promptStr+f"type the series index where your article being placed Or type [new] to create a new series:\n"
        userAction=input(promptStr).strip().lower()
        while True:
            if userAction in indexes or userAction=="new":
                break
            else:
                userAction=input(f"You need to type the series [index] or [new]").strip().lower()
        if userAction=="new":
            creatingFlag,seriesToLandArticle=createNewSeries()
            if not creatingFlag:
                print(seriesToLandArticle)
                sys.exit(0)
        else:
            seriesToLandArticle=allSeries[int(userAction)]

    print(f"You are gonna put your article in series named {seriesToLandArticle.name}")
    
    articles=Article.objects.filter(fromSeries_id=seriesToLandArticle.id).all()
    article=None
    promptStr=""
    if not articles:
        promptStr="There is no articles in this series now.Please create a new one."
        creatingFlag,article=createNewArticle(seriesToLandArticle.id)
        if not creatingFlag:
            print(article)
            sys.exit(0)
    else:
        indexes=[]
        for index,article in enumerate(articles):
            indexes.append(str(index))
            promptStr=promptStr+f"article-index-[{index}]:{article.name}\n"
        promptStr=promptStr+f"type the index of article Or type [new] to create a new article:\n"
        userAction=input(promptStr).strip().lower()
        while True:
            if userAction in indexes or userAction=="new":
                break
            else:
                userAction=input(f"You need to type the article [index] or [new]").strip().lower()
        if userAction=="new":
            creatingFlag,article=createNewArticle(seriesToLandArticle.id)
            if not creatingFlag:
                print(article)
                sys.exit(0)
        else:
            article=articles[int(userAction)]
    articleViewCountObj=ArticleViewCount.objects.get_or_create(article_id=article.id)[0]
    print(f"You are gonna name your article with {article.name} and {article.enName}")

    if not os.path.exists(os.path.join(baseDir,"web","templates","web","docTemplates",f"{seriesToLandArticle.enName}")):
        os.mkdir(os.path.join(baseDir,"web","templates","web","docTemplates",f"{seriesToLandArticle.enName}"))
    if not os.path.exists(os.path.join(baseDir,"web","templates","web","docTemplates",f"{seriesToLandArticle.enName}",f"{article.enName}")):
        os.mkdir(os.path.join(baseDir,"web","templates","web","docTemplates",f"{seriesToLandArticle.enName}",f"{article.enName}"))
    if not os.path.exists(os.path.join(baseDir,"web","static","web","img","docs",f"{seriesToLandArticle.enName}")):
        os.mkdir(os.path.join(baseDir,"web","static","web","img","docs",f"{seriesToLandArticle.enName}"))
    if not os.path.exists(os.path.join(baseDir,"web","static","web","img","docs",f"{seriesToLandArticle.enName}",f"{article.enName}")):
        os.mkdir(os.path.join(baseDir,"web","static","web","img","docs",f"{seriesToLandArticle.enName}",f"{article.enName}"))
    if not os.path.exists(os.path.join(baseDir,"web","static","web","resource","docs",f"{seriesToLandArticle.enName}")):
        os.mkdir(os.path.join(baseDir,"web","static","web","resource","docs",f"{seriesToLandArticle.enName}"))
    if not os.path.exists(os.path.join(baseDir,"web","static","web","resource","docs",f"{seriesToLandArticle.enName}",f"{article.enName}")):
        os.mkdir(os.path.join(baseDir,"web","static","web","resource","docs",f"{seriesToLandArticle.enName}",f"{article.enName}"))
    
    docTemplatePath=os.path.join(baseDir,"web","templates","web","docTemplates",f"{seriesToLandArticle.enName}",f"{article.enName}","doc.html")
    imgDirPath=os.path.join(baseDir,"web","static","web","img","docs",f"{seriesToLandArticle.enName}",f"{article.enName}")

    shutil.rmtree(imgDirPath)
    os.mkdir(imgDirPath)
    print(f"----create a new template file:{docTemplatePath}-------")
    propDir=args.propDir
    if not os.path.exists(propDir):
        print(f"No propDir {propDir} exists. Existing----")
        sys.exit(0)
    for fileName in os.listdir(propDir):
        if fileName.endswith(".html"):
            propHtmlPath=os.path.join(propDir,fileName)
        else:
            assetsDirName=fileName
            assetsDirPath=os.path.join(propDir,fileName)
    copyFilesRecursively(assetsDirPath,imgDirPath)
    print("transfer all the assets file to img dir")
    with open(propHtmlPath,"rt",encoding="utf-8") as f:
        htmlContent=f.read()    
    soup=BeautifulSoup(htmlContent,"html.parser")

    ## title tag
    titleTag=soup.find("title")

    ## replace the id of links in table of contents starting with digit note: on cascade
    tableOfContentsLinks=soup.find_all("a",class_="table_of_contents-link")
    print("============convert a id in nav tag starting with digit===========")
    for link in tableOfContentsLinks:
        href=link.get("href")
        pointId=href[1:]
        if re.match(r"^\d",pointId):
            pointingElem=soup.find(id=pointId)
            pointingElem["id"]="_"+pointId
            link["href"]="#_"+pointId
            print(f"===Detecting:{pointId},processing successfully===")
        else:
            pass   
    print("============Coverting successfully===========")

    ## replace new img src prefix
    print("===Replace prefixes of all img src and according anchor href with  imgDirPath===")
    print(".\n.\n.\n")
    withSrcAttrTags=soup.find_all(findSpecifiedScrAttr)
    for tag in withSrcAttrTags:
        if tag.has_attr("href"):
            tag['href']=tag['href'].replace(quote(assetsDirName), "/".join(["/static","web","img","docs",f"{seriesToLandArticle.enName}",f"{article.enName}"]))
        if tag.has_attr("src"):
            tag["loading"]="lazy"
            tag['src']=tag['src'].replace(quote(assetsDirName),"/".join(["/static","web","img","docs",f"{seriesToLandArticle.enName}",f"{article.enName}"]))
        childrenTags=tag.find_all(findSpecifiedScrAttr)
        for cTag in childrenTags:
            if cTag.has_attr("href"):
                cTag['href']=cTag['href'].replace(quote(assetsDirName),"/".join(["/static","web","img","docs",f"{seriesToLandArticle.enName}",f"{article.enName}"]))
            if cTag.has_attr("src"):
                cTag["loading"]="lazy"
                cTag['src']=cTag['src'].replace(quote(assetsDirName),"/".join(["/static","web","img","docs",f"{seriesToLandArticle.enName}",f"{article.enName}"]))
    print("==============Replaced successfully===============")

    ## if the suffix of src value is common video format, then I should change figure containing this src to a video tag
    print("=========Process to find if has any video source====")
    commonVidFmt = ["mp4", "avi", "mkv", "wmv", "mov", "flv", "webm", "3gp", "3g2", "ogv", "mpeg", "mpg", "divx", "xvid", "h264", "avc", "h265", "hevc"]
    def filterOutVideoSrc(tag):
        if tag.has_attr("href") and tag["href"].split(".")[-1] in commonVidFmt:
            print(f"Found one video source: {tag['href']}")
            return True
        else:
            return False
    videoSrcTags=soup.find_all(filterOutVideoSrc)
    for videoTag in videoSrcTags:
        hrefValue=videoTag["href"]
        hrefFmt=hrefValue.split(".")[-1]
        figureTag=videoTag.find_parent("figure")
        newVidTag=soup.new_tag("video",controls=True,style="display: block; width: 100%; height: 40vh; object-fit: contain;")
        newSrcTag=soup.new_tag("source",src=hrefValue,type=f"video/{hrefFmt}",loading="lazy")
        newVidTag.append(newSrcTag)
        newVidTag.append("Your browser does not support the video tag. Please update to a newer browser.")
        figureTag.clear()
        figureTag.append(newVidTag)
    print("========video tag processing done=========")

    ## wrap the header image in a anchor
    print("=====wrap the page cover image in a anchor and replace anchor href with default no bilibili video img=======")
    print(".\n.\n.\n")
    coverImg=soup.find("img",class_="page-cover-image")
    bilibiliLinkTag=soup.new_tag("a",attrs={
            "target":"_blank"
        })
    if args.bilibiliVidHref=="#":
        coverImg["src"]="/".join(["/static","web","img","nobilibiliVidImg.png"])
        coverImg["style"]="object-position:center 0"
    else:
        bilibiliLinkTag["href"]=args.bilibiliVidHref
    coverImg.wrap(bilibiliLinkTag)
    print(f"=====wrap and replacement with {coverImg['src']} successfully")

    # modify the first two figure tags in the children of .page-body tag referring to datetime tag and view count tag
    pageBodyTag=soup.find("div",class_="page-body")
    dateTimeFigure,viewCountFigure=pageBodyTag.find_all("figure",limit=2)
    timeTag=dateTimeFigure.find("time")
    currentDateTime=datetime.now().strftime("@%B %d, %Y")
    timeTag.string=currentDateTime
    viewCountContainer=viewCountFigure.find("mark",class_="highlight-gray")
    viewCountContainer.string="{{requestedArticleViewCount}}" # need to be rendered from view function

    ## detect the filename of page cover image and add it to article object in database
    coverImgSrc=coverImg["src"]
    print("===========Save the carousel info============")
    docHref=resolve_url("web:docs")+"?docTemplateUrl="+"/".join([seriesToLandArticle.enName,article.enName])
    coverCaptionSeriesName=seriesToLandArticle.name
    coverCaptionArticleName=article.name
    carouselInfo={
        "coverImgSrc":coverImgSrc,
        "docHref":docHref,
        "coverCaptionSeriesName":coverCaptionSeriesName,
        "coverCaptionArticleName":coverCaptionArticleName
    }
    carouselInfoJson=json.dumps(carouselInfo)
    article.carouselInfo=carouselInfoJson
    article.save()
    print("Carousel info:")
    for k,v in carouselInfo.items():
        print(f"{k}:{v}")
    print("=============================================")


    ## add target="_blank" to the some anchor tags
    print("========add target='_blank' declaration to anchors except for nav link======")
    print(".\n.\n.\n")
    anchorTags=soup.find_all(excludeTableOfContentsLink)
    for a in anchorTags:
        a["target"]="_blank"
    print("==========Adding Process Finished=============")
    
    ## add the table and table-responsive class to div.collection-content and delete the anchor target of .cell-title tag
    print("======add the table and table-responsive class to div.collection-content=========")
    print(".\n.\n.\n")
    collectionContentTags=soup.find_all("div",class_="collection-content")
    for tag in collectionContentTags:
        tableTag=tag.find("table")
        tableTag["class"]=" ".join(tableTag["class"]+["table","table-hover"])
        tableResp=soup.new_tag("div",attrs={
            "class":"table-responsive"
        })
        cellTitleTags=tableTag.find_all("td",class_="cell-title")
        for cellTitleTag in cellTitleTags:
            del cellTitleTag.find("a")["href"]
        tag.wrap(tableResp)
    simpleTableTags=soup.find_all("table",class_="simple-table")
    for simpleTable in simpleTableTags:
        tableResp=soup.new_tag("div",attrs={
            "class":"table-responsive"
        })
        simpleTable["class"]=" ".join(simpleTable["class"]+["table","table-hover"])
        simpleTable.wrap(tableResp)
    print("======Adding process complete==========")

    ## add a larger image modal to an image
    print("==========Create larger img modal for each img==========")
    print(".\n.\n.\n")
    def createLargerImgModal(modalId,tag,type):
        '''
            type:1 for figure
                 2 for anchor
        '''
        if type==1:
            anchorTag=tag.find("a")
        elif type==2:
            anchorTag=tag
        anchorTag["href"]=""
        del anchorTag["target"]
        anchorTag["data-bs-target"]="#largerImgModal_"+modalId
        anchorTag["data-bs-toggle"]="modal"
        imgTag=anchorTag.find("img")
        imgSrc=imgTag["src"]
        modalTag=soup.new_tag("div",attrs={
            "class":"modal fade",
            "id":"largerImgModal_"+modalId,
        })
        modalDialogTag=soup.new_tag("div",attrs={
            "class":"modal-dialog modal-fullscreen",
        })
        modalContentTag=soup.new_tag("div",attrs={
            "class":"modal-content positive-relative",
            "data-bs-dismiss":"modal"
        })
        imgTag=soup.new_tag("img",attrs={
            "src":imgSrc,
            "class":"h-100 w-100 object-fit-contain",
            "loading":"lazy"
        })
        modalContentTag.append(imgTag)
        modalDialogTag.append(modalContentTag)
        modalTag.append(modalDialogTag)
        largerImgModalsStr.append(str(modalTag))

    largerImgModalsStr=[]
    
    collectionImgTags=[]
    collectionContentTags=soup.find_all("div",class_="collection-content")
    for tag in collectionContentTags:
        anchorTags=tag.find_all(validateImgWithAnchor)
        for anchorTag in anchorTags:
            collectionImgTags.append(anchorTag)
    figureTags=soup.find_all("figure",class_="image")
    if collectionImgTags or figureTags:
        needsToConstructLargerImgModalsBlock=True
        for tag in figureTags:
            createLargerImgModal(modalId=tag["id"],tag=tag,type=1)
        for tag in collectionImgTags:
            createLargerImgModal(modalId=uuid.uuid4().hex,tag=tag,type=2)
    else:
        needsToConstructLargerImgModalsBlock=False
    
    print("==========Creating completed==========")

    # add some style and attributes to resource download link
    def findResourceDownloadLink(tag):
        if tag.name=="a" and tag.has_attr("href") and tag["href"].endswith("resourceDownload"):
            return True
        else:
            return False
    resourceDownloadLinks=soup.find_all(findResourceDownloadLink)
    for link in resourceDownloadLinks:
        link["class"]="link-secondary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover"
        link["href"]="/".join([r"{% static 'web/resource/docs",seriesToLandArticle.enName,article.enName])+r"' %}"
        del link["target"]
        link["download"]=None


    ## delete some  styles of figure.callout
    calloutTags=soup.find_all("figure",class_="callout")
    for calloutTag in calloutTags:
        calloutTag["style"]="vertical-align:-0.25em"
        calloutTag["class"]=" ".join(calloutTag["class"]+["d-flex","align-items-baseline"])
    
    ## nav tag reconstruct
    print("==========Nav tag reconstruct==========")
    print(".\n.\n.\n")
    navTag=soup.find("nav")
    newNavTag=soup.new_tag("nav",attrs={
        "class":"nav nav-pills flex-column"
    })
    currentIndentation=0
    currentNav=newNavTag
    for div in soup.find_all("div",class_="table_of_contents-item"):
        anchor=div.find("a")
        indentationClass=div.get("class")[-1]
        indentationLevel=int(indentationClass.split("-")[-1])
        navLink=soup.new_tag("a",attrs={
            "class":f'nav-link table_of_contents-indent-{indentationLevel}',
            "href":anchor.get("href")
        })
        anchorContents=list(anchor.contents)
        for i in anchorContents:
            navLink.append(i)
        if indentationLevel>currentIndentation:
            subNav=soup.new_tag("nav",attrs={
                "class":"nav nav-pills flex-column"
            })
            currentNav.append(subNav)
            currentNav=subNav
        elif indentationLevel<currentIndentation:
            for _ in range(currentIndentation-indentationLevel):
                currentNav=currentNav.parent
        else:
            pass
        currentNav.append(navLink)
        currentIndentation=indentationLevel
    navTag.extract()
    articleTag=soup.find("article")
    print("==========Nav tag reconstruct successfully==========")

    # find all the styles with text: @import url("https://cdnjs.cloudflare.com/ajax/libs/KaTeX/\w+/katex.min.css") and extract them from trees
    def findKatexCssTag(tag):
        if tag.name=="style" and bool(re.search(r"https://cdnjs.cloudflare.com/ajax/libs/KaTeX/[0-9.]+/katex\.min\.css",tag.text)):
            return True
        else:
            return False
    katexCssTags=soup.find_all(findKatexCssTag)
    for katexCssTag in katexCssTags:
        katexCssTag.extract()
    needsToImportKatexCss=False
    if katexCssTags:
        importKatexCssTag=soup.new_tag("link")
        importKatexCssTag["rel"]="stylesheet"
        importKatexCssTag["href"]="/static/web/css/notionKatex.css"
        needsToImportKatexCss=True
    # find code tag to see if I need to add prism lib to my code
    needsToImportPrism=False
    preTags=soup.find_all("pre")
    if preTags:
        needsToImportPrism=True
        importPrismCssTag=soup.new_tag("link")
        importPrismCssTag["rel"]="stylesheet"
        importPrismCssTag["href"]="/static/web/css/prism.min.css"
        importPrismJsTag=soup.new_tag("script")
        importPrismJsTag["src"]="/static/web/js/prism.min.js"
        for pre in preTags:
            pre["class"]="line-numbers"
            code=pre.find("code")
            codeString=code.string
            if codeString.startswith("language-"):
                language=re.findall(r"^language-(\w+)\n",codeString)[0]
                print(f"===Detect a code block with language {language}===")
                code["class"]=f"language-{language}"
                code.string=re.sub(r"^language-(\w+)\n","",codeString)
            else:
                print("===No language detected from this code block===")
                code["class"]=f"language-none"
    # construct the contents in css block and js block and largerImgModals block
    cssBlockTagContents=""
    jsBlockTagContents=""
    largerImgModalsContents=""

    if needsToImportKatexCss:
        cssBlockTagContents+=str(importKatexCssTag)
    if needsToImportPrism:
        cssBlockTagContents+=str(importPrismCssTag)
        jsBlockTagContents+=str(importPrismJsTag)
    if needsToConstructLargerImgModalsBlock:
        largerImgModalsContents=largerImgModalsContents.join(largerImgModalsStr)


    ## write new html file
    with open(docTemplatePath,"wt",encoding="utf-8") as f:
        f.write("{% extends 'web/layout/docLayout.html' %}{% load static %}{% load i18n %}")
        f.write("{% block title %}\n"+str(titleTag)+"{% endblock %}\n")
        f.write("{% block css %}\n"+str(cssBlockTagContents)+"{% endblock %}\n")
        f.write("{% block tableOfContents %}\n"+str(newNavTag)+"{% endblock %}\n")
        f.write("{% block content %}\n"+str(articleTag)+"{% endblock %}\n")
        f.write("{% block largerImgModalContainer %}\n"+str(largerImgModalsContents)+"{% endblock %}\n")
        f.write("{% block js %}\n"+str(jsBlockTagContents)+"{% endblock %}")
else:
    print("Exit for wrong argument input")
    sys.exit(0)


