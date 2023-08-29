# Project Name: liaozhiMe

description: My personal website

## Table of Contents

- [Introduction](#introduction)
- [Deployment](#deployment)

## Introduction

This is my personal website, which can be accessed through [liaozhiMe](https://liaozhi.me)

## Deployment

This is steps when you deploy project in production environment:
 what need to be modified in production environment:
 1. make a copy of localSettingsTemplate and configure it
 2. change Debug value to False
 3. add the domain associated with server to ALLOWED_HOST
 4. (optional) if you use digitalocean cloud server or any other cloud server service that can add external storage to your server and you want to place your staticfiles in the external storage, you need to add the dir path to STATICFILES_DIRS and run cmd 'python manage.py collectstatic' to collect the static files into staticfiles dir.
 5. As a admin, you need to follow next methods to add bilibili video resource and bilibili video docs
    for adding bilibili video resource, you need to create or select the videoSeries and video to which the resource belong. Note:
    the name of videoSeries and video should be Chinese and the url of resource in machine(in staticfiles dir) should be composition of
    English type of videoSeries name and video name, and you can name the url composition arbitrary value and then just the put relative url of 
    resource in the resource url field
    for adding bilibili video docs, you need to create docs template index like this
    web/templates/web/bilibiliVideoDocTemplates/3(videoSeriesId)/2(videoId)/doc.html

