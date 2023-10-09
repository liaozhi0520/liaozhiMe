import argparse
import os,re,sys,shutil
from bs4 import BeautifulSoup
from urllib.parse import quote

baseDir=os.path.dirname(__file__)
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
    ## replace the id of links in table of contents starting with digit note: on cascade
    tableOfContentsLinks=soup.find_all("a",class_="table_of_contents-link")
    for link in tableOfContentsLinks:
        href=link.get("href")
        pointId=href[1:]
        if re.match(r"^\d",pointId):
            pointingElem=soup.find(id=pointId)
            pointingElem["id"]="_"+pointId
            link["href"]="#_"+pointId
        else:
            pass

    ## replace new img src prefix
    def findSpecifiedScrAttr(tag):
        if (tag.has_attr("href") and tag['href'].startswith(quote(assetsDirName))) or (tag.has_attr("src") and tag['src'].startswith(quote(assetsDirName))):
            return True
        else:
            return False
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
    ## reformat title tag

    titleTag=soup.find("title")
    titleTagContent=titleTag.string
    titleTag.string="{% trans "+"'"+titleTagContent+"' "+"%}"
    print(f"---new title tag:{titleTag.prettify()}----")

    ## add target="_blank" to the some anchor tags
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
    anchorTags=soup.find_all(excludeTableOfContentsLink)
    for a in anchorTags:
        a["target"]="_blank"
    
    ## wrap the header image in a anchor
    coverImg=soup.find("img",class_="page-cover-image")
    bilibiliLinkTag=soup.new_tag("a",attrs={
            "target":"_blank"
        })
    if args.bilibiliVidHref=="#":
        bilibiliLinkTag["href"]="#"
        coverImg["src"]="{% static 'web/img/nobilibiliVidImg.png' %}"
        coverImg["style"]="object-position:center 0"
    else:
        bilibiliLinkTag["href"]=args.bilibiliVidHref
    bilibiliLinkTag.append(coverImg)
    soup.find("header").insert(0,bilibiliLinkTag)

    ## delete some  styles of figure.callout
    calloutTags=soup.find_all("figure",class_="callout")
    for calloutTag in calloutTags:
        calloutTag["style"]='display:flex'
    ## nav tag reconstruct
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



else:
    print("Exit for wrong argument input")
    sys.exit(0)


