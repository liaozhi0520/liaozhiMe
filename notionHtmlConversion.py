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
from web.models import Video
from django.shortcuts import resolve_url
import json


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


parser=argparse.ArgumentParser(description="This is a python script for converting the exported notion html to my own blog html")
parser.add_argument("-p","--propDir", type=str, required=True, help="Input path of the dir including the exported notion html.")
parser.add_argument("-b","--bilibiliVidHref",required=False, default="#",type=str,help="If you got a bilibili video for this tutorial, then you can input one, otherwise it is set to #")
parser.add_argument("-n","--tutorialNo",required=True,type=str,help="this is should be a format like videoSeriesId/videoId")
args=parser.parse_args()
checkInput=input(f"This is the arguments you input, please check it again:\n--propDir:{args.propDir}\n--bilibiliVidHref:{args.bilibiliVidHref}\n--tutorialNo:{args.tutorialNo}\n[y|n]").strip().lower()
while True:
    if not re.match(r"y|n",checkInput):
        checkInput=input(f"Please input y or n").strip().lower()
    else:
        break
if checkInput=="y":
    tuturialNo=args.tutorialNo.split(r"/")
    templatePath=os.path.join(baseDir,"web","templates","web","bilibiliVideoDocTemplates",tuturialNo[0],tuturialNo[1],"doc.html")
    imgDirPath=os.path.join(baseDir,"web","static","web","img","bilibiliVideoDocTemplates",tuturialNo[0],tuturialNo[1])
    if not os.path.exists(os.path.join(baseDir,"web","templates","web","bilibiliVideoDocTemplates",tuturialNo[0])):
        os.mkdir(os.path.join(baseDir,"web","templates","web","bilibiliVideoDocTemplates",tuturialNo[0]))
    if not os.path.exists(os.path.join(baseDir,"web","templates","web","bilibiliVideoDocTemplates",tuturialNo[0],tuturialNo[1])):
        os.mkdir(os.path.join(baseDir,"web","templates","web","bilibiliVideoDocTemplates",tuturialNo[0],tuturialNo[1]))
    if not os.path.exists(os.path.join(baseDir,"web","static","web","img","bilibiliVideoDocTemplates",tuturialNo[0])):
        os.mkdir(os.path.join(baseDir,"web","static","web","img","bilibiliVideoDocTemplates",tuturialNo[0]))
    if not os.path.exists(os.path.join(baseDir,"web","static","web","img","bilibiliVideoDocTemplates",tuturialNo[0],tuturialNo[1])):
        os.mkdir(os.path.join(baseDir,"web","static","web","img","bilibiliVideoDocTemplates",tuturialNo[0],tuturialNo[1]))
    shutil.rmtree(imgDirPath)
    os.mkdir(imgDirPath)
    print(f"----create a new template file:{templatePath}-------")
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
    print("===Replace prefixes of all img src and according anchor href with {% static imgUrlPrefix %}===")
    print(".\n.\n.\n")
    withSrcAttrTags=soup.find_all(findSpecifiedScrAttr)
    for tag in withSrcAttrTags:
        if tag.has_attr("href"):
            tag['href']=tag['href'].replace(quote(assetsDirName),'{% static imgUrlPrefix %}')
        if tag.has_attr("src"):
            tag['src']=tag['src'].replace(quote(assetsDirName),'{% static imgUrlPrefix %}')
        childrenTags=tag.find_all(findSpecifiedScrAttr)
        for cTag in childrenTags:
            if cTag.has_attr("href"):
                cTag['href']=cTag['href'].replace(quote(assetsDirName),'{% static imgUrlPrefix %}')
            if cTag.has_attr("src"):
                cTag['src']=cTag['src'].replace(quote(assetsDirName),'{% static imgUrlPrefix %}')
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
        newSrcTag=soup.new_tag("source",src=hrefValue,type=f"video/{hrefFmt}")
        newVidTag.append(newSrcTag)
        newVidTag.append("Your browser does not support the video tag. Please update to a newer browser.")
        figureTag.clear()
        figureTag.append(newVidTag)
    print("========video tag processing done=========")

    ## wrap the header image in a anchor
    print("=====wrap the header image in a anchor and replace anchor href with default no bilibili video img=======")
    print(".\n.\n.\n")
    coverImg=soup.find("img",class_="page-cover-image")
    bilibiliLinkTag=soup.new_tag("a",attrs={
            "target":"_blank"
        })
    if args.bilibiliVidHref=="#":
        coverImg["src"]="{% static 'web/img/nobilibiliVidImg.png' %}"
        coverImg["style"]="object-position:center 0"
    else:
        bilibiliLinkTag["href"]=args.bilibiliVidHref
    coverImg.wrap(bilibiliLinkTag)
    print(f"=====wrap and replacement with {coverImg['src']} successfully")

    ## detect the filename of page cover image and add it to video object in database
    print("===========Save the carousel info============")
    coverImgSrc=coverImg["src"]
    if coverImgSrc=="{% static 'web/img/nobilibiliVidImg.png' %}":
        coverImgSrc='/'.join(["/static"]+re.findall(r"{% static '(.*)' %}",coverImgSrc,re.DOTALL))
    else:
        coverImgSrc="/".join(["/static","web/img/bilibiliVideoDocTemplates"]+tuturialNo+[coverImgSrc.split("/",1)[1]]) 
    docHref=resolve_url("web:bilibiliVideoDocs")+"?docTemplateUrl="+"web/bilibiliVideoDocTemplates/"+tuturialNo[0]+"/"+tuturialNo[1]
    vidObj=Video.objects.get(id=tuturialNo[1])
    coverCaptionSeriesName=vidObj.fromSeires.seriesName
    coverCaptionVideoName=vidObj.videoName
    carouselInfo={
        "coverImgSrc":coverImgSrc,
        "docHref":docHref,
        "coverCaptionSeriesName":coverCaptionSeriesName,
        "coverCaptionVideoName":coverCaptionVideoName
    }
    carouselInfoJson=json.dumps(carouselInfo)
    vidObj.carouselInfo=carouselInfoJson
    vidObj.save()
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
            "class":"h-100 w-100 object-fit-contain"
        })
        modalContentTag.append(imgTag)
        modalDialogTag.append(modalContentTag)
        modalTag.append(modalDialogTag)
        largerImgModals.append(modalTag.prettify())

    largerImgModals=[]
    collectionImgTags=[]
    figureTags=soup.find_all("figure",class_="image")
    ## I found that the image abemmded in the .collection-content don't have the figure tag to include it. I need to find a way to detect that
    collectionContentTags=soup.find_all("div",class_="collection-content")
    for tag in collectionContentTags:
        anchorTags=tag.find_all(validateImgWithAnchor)
        for anchorTag in anchorTags:
            collectionImgTags.append(anchorTag)
    
    for tag in figureTags:
        createLargerImgModal(modalId=tag["id"],tag=tag,type=1)
    for tag in collectionImgTags:
        createLargerImgModal(modalId=uuid.uuid4().hex,tag=tag,type=2)
    print("==========Creating completed==========")

    ## delete some  styles of figure.callout
    calloutTags=soup.find_all("figure",class_="callout")
    for calloutTag in calloutTags:
        calloutTag["style"]='display:flex'
    
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


    ## write new html file
    with open(templatePath,"wt",encoding="utf-8") as f:
        f.write('''
{% extends 'web/layout/docLayout.html' %}
{% load static %}
{% load i18n %}
''')
        f.write("{% block title %}\n"+titleTag.prettify()+"{% endblock %}\n")
        f.write("{% block tableOfContents %}\n"+newNavTag.prettify()+"{% endblock %}\n")
        f.write("{% block content %}\n"+articleTag.prettify()+"{% endblock %}\n")
        largerImgModalsStr="{% block largerImgModalContainer %}\n"
        for modal in largerImgModals:
            largerImgModalsStr+=modal
        largerImgModalsStr+="{% endblock %}"
        f.write(largerImgModalsStr)



else:
    print("Exit for wrong argument input")
    sys.exit(0)


