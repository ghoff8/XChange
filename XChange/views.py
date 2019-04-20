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
import matplotlib.pyplot as plt
from pylab import *
import PIL, PIL.Image, StringIO
import base64
from io import BytesIO
import requests
import json
from datetime import datetime

from .forms import SignUpForm, LoginForm
from .models import UserProfile, Bookmark, Asset
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
            userNew = authenticate(username=username, password=raw_password)
            newlyCreatedProf = UserProfile.objects.create(user = userNew)
            Asset.objects.create(userProfile = newlyCreatedProf, assetName = 'USD', shares = 1000, timeBought = datetime.now().strftime('%Y-%m-%d'), priceBought = 1.00)
            djLogin(request, userNew)
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
            results = []
            if (search_data):
                try:
                    #currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + str(search_data).strip() + '/quote?displayPercent=true')
                    nameSearch = requests.get(djSettings.DATA_ENDPOINT + '/ref-data/symbols')
                except requests.exceptions.RequestException:
                    error = "Error: " + str(nameSearch.status_code)
                    return render(request, 'XChange/search.html', {'error': error})
                if(nameSearch.status_code == 200):
                    nameJsonData = json.loads(nameSearch.content)
                    for pos, x in enumerate(nameJsonData):
                        if (str(search_data).lower() in x['name'].lower() or str(search_data).lower() in x['symbol'].lower()):
                            symbol = x['name']
                            currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + str(x['symbol']) + '/quote?displayPercent=true')
                            symJsonData = json.loads(currentSearch.content)
                            currentPrice = symJsonData['latestPrice']
                            currentGrowth = symJsonData['changePercent']
                            currentChange = symJsonData['change']
                            results.append({"symbol": x['name'], "currentPrice": symJsonData['latestPrice'], "currentGrowth": symJsonData['changePercent'], "currentChange": symJsonData['change']})
                    if (not results):
                        error = "No Results"
                        return render(request, 'XChange/search.html', {'error': error})
                    return render(request, 'XChange/search.html', {'results': results})
                else:
                    error = "Asset Not Found"
                    return render(request, 'XChange/search.html', {'error': error})
            else:
                error = "Please enter an asset symbol or company name"
                return render(request, 'XChange/search.html', {'error': error})
            
    return render(request, 'XChange/search.html')

def bookmarks(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    currentProfile = UserProfile.objects.get(user = request.user)
    userBookmarks = Bookmark.objects.filter(userProfile = currentProfile).order_by('companyName')
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
        elif(request.POST.get('delete')):
            bmID = request.POST['delete']
            Bookmark.objects.filter(id=bmID).delete()
            message = 'Bookmark deleted'
            return render(request, 'XChange/bookmarks.html', {'userBookmarks': userBookmarks, 'message': message})
    return render(request, 'XChange/bookmarks.html', {'userBookmarks': userBookmarks})
    
def home(request):
   
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    graphic = None
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
        
    #graphic = getGraph(request, None).content
    return render(request, 'XChange/home.html', {'graphic': graphic, 'cryptoTop': cryptoTop, 'stockMovers': stockMovers})
    
def myPortfolio(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    graphic = None
    currentProfile = UserProfile.objects.get(user = request.user)
    userAssets = Asset.objects.filter(userProfile = currentProfile)
    userBookmarks = Bookmark.objects.filter(userProfile = currentProfile).distinct()
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
        elif(request.POST.get('assetGraph')):
            stockReq = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + str(request.POST['assetGraph']).strip() + '/chart/1m').content
            stockChartData = json.loads(stockReq)
            for pos, obj in enumerate(stockChartData):
                date = obj.pop('label', None)
                close = float(obj.pop('close', None))
                data = {u'label': date, u'close': close, u'pos': int(pos)}
                stockChartData[pos] = data
            graphic = getGraph(request, stockChartData).content
            selectedAsset = Asset.objects.get(userProfile = currentProfile, assetName = request.POST['assetGraph'])
            return render(request, 'XChange/myPortfolio.html', {'userAssets': userAssets, 'userBookmarks': userBookmarks, 'graphic': graphic, 'selectedAsset': selectedAsset})
    return render(request, 'XChange/myPortfolio.html', {'userAssets': userAssets, 'userBookmarks': userBookmarks})    


def getGraph(request, data):
    
    fig = plt.figure(figsize=(9, 4))
    ax = fig.add_subplot(111, frameon=False)
    xPlots = []
    yPlots = []
    xTicks = []
    
    for obj in data:
        xPlots.append(obj['pos'])
        yPlots.append(obj['close'])
        xTicks.append(str(obj['label']))
    ax.plot(xPlots, yPlots, 'g', linewidth= 3)
    ax.set_xticks(np.arange(min(xPlots),max(xPlots)+1, 1.0))
    
    ax.set_xticklabels(xTicks, rotation='vertical', fontsize=10)

    ax.set_xlabel('Day')
    ax.set_ylabel('Price')
    

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