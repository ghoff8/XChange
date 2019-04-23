# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, default=0)
    
class Asset(models.Model):
    userProfile = models.ForeignKey(UserProfile)
    assetName = models.CharField(max_length=250)
    timeBought = models.DateTimeField()
    shares = models.FloatField(max_length=250)
    priceBought = models.FloatField(max_length=250)
    
class Bookmark(models.Model):
    userProfile = models.ForeignKey(UserProfile)
    companyName = models.CharField(max_length=250)
    setDate = models.DateTimeField()
    bookmarkPrice = models.FloatField(max_length=250)
    bookmarkAmount = models.IntegerField(max_length=250)


    
    