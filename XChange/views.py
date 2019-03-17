# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'XChange/index.html')

def login(request):
    return render(request, 'XChange/login.html')
    
def settings(request):
    return render(request, 'XChange/settings.html')
    
def bookmarks(request):
    return render(request, 'XChange/bookmarks.html')