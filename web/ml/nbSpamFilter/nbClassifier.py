import pandas as pd
import numpy as np
import os
import sys
import re
import argparse
import subprocess
import platform
import django

parser=argparse.ArgumentParser(description="This is a script to inference the spam filter")
parser.add_argument("-e","--emailId",type=str,required=True,help="Input the Email id You want to classify")
parser.add_argument("-b","--baseDir",type=str,required=True,help="Input the baseDir of your project")
args=parser.parse_args()
emailId=args.emailId
baseDir=args.baseDir

sys.path.append(baseDir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','liaozhiMe.settings')
django.setup()
from web.models import SpamCheckResUserFeedback
spamCheckResUserFeedbackObj=SpamCheckResUserFeedback.objects.get(id=emailId)


emailTypeFreqCsvPath=os.path.join(baseDir,"web","ml","nbSpamFilter","data","emailTypeFreq.csv")
vocabFreqCsvPath=os.path.join(baseDir,"web","ml","nbSpamFilter","data","vocabFreq.csv")
emailTypeFreqDf=pd.read_csv(emailTypeFreqCsvPath)
vocabFreqDf=pd.read_csv(vocabFreqCsvPath)
hamFreq=emailTypeFreqDf.iloc[0,0]
spamFreq=emailTypeFreqDf.iloc[0,1]
hamCount=emailTypeFreqDf.iloc[0,2]
spamCount=emailTypeFreqDf.iloc[0,3]

def classifyEmail(emailToBeClassified):
	# extract all words out of email to be classified
	sanitizedEmail=re.sub(r"<[^>]*>"," ",emailToBeClassified)
	wordsOfEmail=re.findall(r"\b\w+\b",sanitizedEmail)
	stopWords=set(["and", "the", "in", "to", "for", "on", "with", "that"])
	wordsOfEmail=[word for word in wordsOfEmail if word not in stopWords ]

	freqInHamOfWords=[]
	freqInSpamOfWords=[]
	for word in wordsOfEmail:
		rowInVocabOfWord=vocabFreqDf[vocabFreqDf.iloc[:,0]==word]
		if rowInVocabOfWord.size>0:
			freqInHamOfWords.append(rowInVocabOfWord.iloc[0,1])
			freqInSpamOfWords.append(rowInVocabOfWord.iloc[0,2])
		else:
			freqInHamOfWords.append(1/(2+hamCount)) #1/4829
			freqInSpamOfWords.append(1/(2+spamCount)) #1/749

	productForFreqInHamOfWords=np.prod(freqInHamOfWords)
	productForFreqInSpamOfWords=np.prod(freqInSpamOfWords)
	probToSpam=productForFreqInSpamOfWords*spamFreq/(productForFreqInHamOfWords*hamFreq+productForFreqInSpamOfWords*spamFreq)
	probToHam=productForFreqInHamOfWords*hamFreq/(productForFreqInHamOfWords*hamFreq+productForFreqInSpamOfWords*spamFreq)
	if probToSpam>probToHam:
		classificationCode="1"
	else:
		classificationCode="0"
	print(f"emailType: {classificationCode}")
	return classificationCode

classificationCode=classifyEmail(spamCheckResUserFeedbackObj.email)
spamCheckResUserFeedbackObj.checkRes=classificationCode
spamCheckResUserFeedbackObj.save()