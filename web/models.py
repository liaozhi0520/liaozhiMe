from django.db import models


# Create your models here.

class Series(models.Model):
    enName=models.CharField(max_length=128,unique=True) # used for creating the url
    name=models.CharField(max_length=128, unique=True)
    createdAt=models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    enName=models.CharField(max_length=128) # used for creating the url
    name=models.CharField(max_length=128)
    fromSeries=models.ForeignKey(to='Series',on_delete=models.CASCADE)
    showingAtLandingPage=models.BooleanField(default=False)
    showingFirstly=models.BooleanField(default=False)
    carouselInfo=models.CharField(max_length=3000,default=None) ## json format info
    createdAt=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=["enName","fromSeries"],name="unique enName of article in a series"),
            models.UniqueConstraint(fields=["name","fromSeries"],name="unique Name of article in a series")
        ]


class Notification(models.Model):
    NOTIFICATIONTYPE=(
        ('normal','normal'),
        ('danger','danger')
    )
    type=models.CharField(max_length=10,choices=NOTIFICATIONTYPE)
    text=models.CharField(max_length=1000)
    createdAt=models.DateTimeField(auto_now_add=True)

class SpamCheckResUserFeedback(models.Model):
    CHECKRESCHOICES=(
        ('1','spamEmail'),
        ('0','normalEmail'),
        ('notSet',"notSet")
    )
    USERFEEDBACKCHOICES=(
        ('1','spamEmail'),
        ('0','normalEmail'),
        ('notSet',"notSet")
    )
    email=models.CharField(max_length=1000)
    checkRes=models.CharField(default="notSet",choices=CHECKRESCHOICES,max_length=6)
    userFeedback=models.CharField(default="notSet",choices=USERFEEDBACKCHOICES,max_length=6)
    createdAt=models.DateTimeField(auto_now_add=True)

class ArticleViewCount(models.Model):
    count=models.BigIntegerField(default=101)
    article=models.ForeignKey(to="Article",on_delete=models.CASCADE)
    lastViewerAt=models.DateTimeField(auto_now=True)


    

