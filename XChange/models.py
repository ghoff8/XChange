# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Users(models.Model):
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    email = models.CharField(max_length=250)

class Assests(models.Model):
    stockName = models.CharField(max_length=250)
    amount = models.CharField(max_length=250)
    priceBought = models.CharField(max_length=250)
    
class Stocks(models.Model):
    compName = models.CharField(max_length=250)
    stockPrice = models.CharField(max_length=250)
    stockTime = models.CharField(max_length=250)
    stockAmount = models.CharField(max_length=250)
    
class Crypto(models.Model):
    compName = models.CharField(max_length=250)
    cryptoPrice = models.CharField(max_length=250)
    cryptoTime = models.CharField(max_length=250)
    cryptoAmount = models.CharField(max_length=250)
    
class Bookmarks(models.Model):
    compName = models.CharField(max_length=250)
    bookmarkPrice = models.CharField(max_length=250)
    setDate = models.CharField(max_length=250)
    bookmarkAmount = models.CharField(max_length=250)
