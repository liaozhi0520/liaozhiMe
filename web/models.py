from django.db import models


# Create your models here.

class VideoSeries(models.Model):
    seriesName=models.CharField(max_length=128, unique=True)
    createdAt=models.DateTimeField(auto_now_add=True)

class Video(models.Model):
    videoName=models.CharField(max_length=128,unique=True)
    fromSeires=models.ForeignKey(to='VideoSeries',on_delete=models.CASCADE)
    showingAtLandingPage=models.BooleanField(default=False)
    showingFirstly=models.BooleanField(default=False)
    carouselInfo=models.CharField(max_length=3000,default=None) ## json format info
    createdAt=models.DateTimeField(auto_now_add=True)

class Resource(models.Model):
    resourceName=models.CharField(max_length=128,unique=True)
    resourceUrl=models.CharField(max_length=255,unique=True)
    fromVideo=models.ForeignKey(to='Video',on_delete=models.CASCADE)
    createdAt=models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    NOTIFICATIONTYPE=(
        ('normal','normal'),
        ('danger','danger')
    )
    type=models.CharField(max_length=10,choices=NOTIFICATIONTYPE)
    text=models.CharField(max_length=1000)
    createdAt=models.DateTimeField(auto_now_add=True)
