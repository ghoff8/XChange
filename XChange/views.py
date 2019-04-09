# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings as djSettings
from django.contrib.auth import login as djLogin, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from matplotlib import pylab
from pylab import *
import PIL, PIL.Image, StringIO
import base64
from io import BytesIO
import requests
import json
from decimal import Decimal

from .forms import SignUpForm, LoginForm
# Create your views here.

def index(request):
    return render(request, 'XChange/index.html')

def login(request):
    if request.method == 'POST' and request.POST.get('submit') == "register":
        login_form = AuthenticationForm()
        reg_form = SignUpForm(request.POST)
        if reg_form.is_valid():
            reg_form.save()
            username = reg_form.cleaned_data.get('username')
            raw_password = reg_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            djLogin(request, user)
            return redirect('home')
    
    elif request.method == 'POST' and request.POST.get('submit') == "login": 
        login_form =  AuthenticationForm(request.POST)
        reg_form = SignUpForm()
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            djLogin(request, user)
            return redirect("home")
        else:
            return render(request, 'XChange/login.html', {'login_form': login_form, 'reg_form': reg_form, 'error': 'Login Failed'})
    else:
        login_form = LoginForm()
        reg_form = SignUpForm()
    return render(request, 'XChange/login.html', {'login_form': login_form, 'reg_form': reg_form})
    
def settings(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
    return render(request, 'XChange/settings.html')
    
def search(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
        
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Search'):
            search_data = request.POST['searchText']
            currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + str(search_data).strip() + '/quote?displayPercent=true')
            if (currentSearch.status_code == 200):
                jsonData = json.loads(currentSearch.content)
                symbol = jsonData['companyName']
                currentPrice = jsonData['latestPrice']
                currentGrowth = jsonData['changePercent']
                currentChange = jsonData['change']
                return render(request, 'XChange/search.html', {'currentSearch': currentSearch, 'currentPrice': currentPrice, 'symbol': symbol, 'currentGrowth': currentGrowth, 'change': currentChange})
            else:
                error = "Asset Not Found"
                return render(request, 'XChange/search.html', {'error': error})
            
    return render(request, 'XChange/search.html')

def bookmarks(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
    return render(request, 'XChange/bookmarks.html')
    
def home(request):
   
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
    else:
        stockReq = requests.get(djSettings.DATA_ENDPOINT + '/stock/market/list/gainers').content
        stockMovers = json.loads(stockReq)
        cryptoReq = requests.get(djSettings.DATA_ENDPOINT + '/stock/market/crypto').content
        cryptoTop = json.loads(cryptoReq)
        for x in cryptoTop:
            x['changePercent'] *= 100
        for x in stockMovers:
            x['changePercent'] *= 100
        del cryptoTop[5]   #delete bad data
        del cryptoTop[14]
        
    graphic = getGraph(request).content
    return render(request, 'XChange/home.html', {'graphic': graphic, 'cryptoTop': cryptoTop, 'stockMovers': stockMovers})
    
def myPortfolio(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
    return render(request, 'XChange/myPortfolio.html')    


def getGraph(request):
    pos = np.arange(10)+ 2 

    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111)

    ax.barh(pos, np.arange(1, 11), align='center')
    ax.set_yticks(pos)
    ax.set_yticklabels(('#hcsm',
        '#ukmedlibs',
        '#ImmunoChat',
        '#HCLDR',
        '#ICTD2015',
        '#hpmglobal',
        '#BRCA',
        '#BCSM',
        '#BTSM',
        '#OTalk',), 
        fontsize=15)
    ax.set_xticks([])
    ax.invert_yaxis()

    ax.set_xlabel('Popularity')
    ax.set_ylabel('Hashtags')
    ax.set_title('Hashtags')

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    # Send buffer in a http response the the browser with the mime type image/png set
    return HttpResponse(graphic, content_type="image/png")