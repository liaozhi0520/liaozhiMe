from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from web.forms.docApis.nbSpamFilter import SpamCheckForm
from web.models import SpamCheckResUserFeedback
from liaozhiMe.settings import BASE_DIR as baseDir
import os
import subprocess
from django.utils.translation import gettext as _
import platform
import re


class SpamCheckView(View):
    def post(self,request,*args,**kwargs):
        spamCheckForm=SpamCheckForm(request.POST)
        if spamCheckForm.is_valid():
            cleanedData=spamCheckForm.cleaned_data
            spamToCheck=cleanedData["spamToCheck"]
            # use subprocess to get the res of spam check
            spamCheckResUserFeedbackObj=SpamCheckResUserFeedback.objects.create(
                email=spamToCheck
            )
            nbClassifierScript=os.path.join(baseDir,"web","ml","nbSpamFilter","nbClassifier.py")
            if platform.system()=="Windows":
                runCmd=f'{os.path.join(os.path.dirname(baseDir),"venv","Scripts","activate.bat")} && python {nbClassifierScript} -e {str(spamCheckResUserFeedbackObj.id)} -b {baseDir}'
            elif platform.system()=="Linux":
                runCmd=f'source {os.path.join(os.path.dirname(baseDir),"venv","bin","activate")} && python {nbClassifierScript} -e {str(spamCheckResUserFeedbackObj.id)} -b {baseDir}'
            print(f"{runCmd}")
            cmdResult=subprocess.run(runCmd,capture_output=True,text=True,shell=True)
            if cmdResult.returncode==0:
                sucOutput=cmdResult.stdout
                emailType=re.findall(r"emailType: (\d{1})",sucOutput)[0]
                res={
                    "content":[
                        {
                            "fieldFlag":True,
                            "fieldName":"spamToCheck",
                            "fieldValidationRes":_("We may give the email a label: spam") if emailType=="1" else _("We may give the email a label: normal")
                        }
                    ]
                }
                request.session["emailId"]=spamCheckResUserFeedbackObj.id
            else:
                errorMsg=cmdResult.stderr
                res={
                    "content":[
                        {
                            "fieldFlag":False,
                            "fieldName":"spamToCheck",
                            "fieldValidationRes":_("Something unexpected error occurred from server: ")+errorMsg
                        }
                    ]
                }
        else:
            res={
                "content": [
                    {
                        "fieldFlag":False,
                        "fieldName":field,
                        "fieldValidationRes":errorMsg
                    }
                    for field,errorMsg in spamCheckForm.errors.items()
                ]
            }
        return JsonResponse(safe=False,data=res)

class SpamFilterResUserFeedbackView(View):
    def post(self,request,*args,**kwargs):
        postData=request.POST
        emailId=request.session["emailId"]
        userFeedback=postData.get("userFeedback")
        # validate emailId is equal to the request.session["emailId"] and userFeedback is in ["spamCheckResIsCorrect","spamCheckResIsInCorrect"]
        if userFeedback in ["spamCheckResUserFeedbackIsCorrect","spamCheckResUserFeedbackIsInCorrect"]:
            postDataIsValid=True
        else:
            postDataIsValid=False
        if postDataIsValid:
            spamCheckResUserFeedbackObj=SpamCheckResUserFeedback.objects.get(id=emailId)
            if userFeedback=="spamCheckResUserFeedbackIsCorrect":
                spamCheckResUserFeedbackObj.userFeedback=spamCheckResUserFeedbackObj.checkRes
            else:
                choice=["1","0"]
                choice.remove(spamCheckResUserFeedbackObj.checkRes)
                spamCheckResUserFeedbackObj.userFeedback=choice[0]
            spamCheckResUserFeedbackObj.save()
            res=None
        else:
            res=None
        return JsonResponse(res,safe=False)