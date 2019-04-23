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
import operator
from .forms import SignUpForm, LoginForm, SettingsPasswordForm
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
        # settingspass_form = SettingsPasswordForm()
        
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
            
        if request.method == 'POST' and request.POST.get('settsubmit'):
            settingspass_form = SettingsPasswordForm(request.user, request.POST)
            print("before valid print statement")
            if settingspass_form.is_valid():
                raw_password = settingspass_form.cleaned_data.get('password1')
                user = settingspass_form.save()
                userNew = authenticate(username=user.username, password=raw_password)
                # djLogin(request, userNew)
                print("password changed")
                return redirect('/login.html')
		
            
    else:
          
        settingspass_form = SettingsPasswordForm(request.user)
        print("password not changed")
        return render(request, 'XChange/settings.html', {
            'settingspass_form': settingspass_form})
                
    
    return render(request, 'XChange/settings.html', {'settingspass_form': settingspass_form})
    
def search(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
        
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
        elif (request.POST.get('submit') == 'Search'):
            search_data = request.POST['searchText']
            results = []
            if (search_data):
                try:
                    nameSearch = requests.get(djSettings.DATA_ENDPOINT + '/ref-data/symbols')
                except requests.exceptions.RequestException:
                    error = "Error: " + str(nameSearch.status_code)
                    return render(request, 'XChange/search.html', {'error': error})
                if(nameSearch.status_code == 200):
                    nameJsonData = json.loads(nameSearch.content)
                    for pos, x in enumerate(nameJsonData):
                        if ((str(search_data).lower() in x['name'].lower() or str(search_data).lower() in x['symbol'].lower()) and not (x['symbol'] == 'BCCUSDT' or x['symbol'] == 'VENUSDT')):
                            currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + str(x['symbol']) + '/quote?displayPercent=true')
                            symJsonData = json.loads(currentSearch.content)
                            results.append({"symbol": x['symbol'], "name": x['name'], "currentPrice": symJsonData['latestPrice'], "currentGrowth": symJsonData['changePercent'], "currentChange": symJsonData['change']})
                    if (not results):
                        error = "No Results"
                        return render(request, 'XChange/search.html', {'error': error})
                    return render(request, 'XChange/search.html', {'results': results})
                else:
                    error = "Asset Not Found"
                    return render(request, 'XChange/search.html', {'error': error})
            else:
                error = "Please enter an asset symbol, cryptocurrency, or company name"
                return render(request, 'XChange/search.html', {'error': error})
            
    return render(request, 'XChange/search.html')

def assetDetails(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    currentUser = UserProfile.objects.get(user = request.user)
    currentBalance = Asset.objects.get(assetName = 'USD', userProfile = currentUser)
    currentBalanceAmount = round(currentBalance.shares * currentBalance.priceBought, 2)
    error = None
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return redirect('index')
        elif(request.POST.get('buyButton')):
            asset = request.GET.get('asset')
            totalBuy = float(request.POST.get('buyButton'))
            shares = request.POST.get('numOfShares')
            if (shares):
                currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + asset + '/quote?displayPercent=true')
                currentPrice = json.loads(currentSearch.content)['latestPrice']
                if (totalBuy < currentBalanceAmount):
                    existingCheck = Asset.objects.filter(assetName = asset, userProfile = currentUser)
                    if(existingCheck):
                        pass #TODO
                    else:
                        newlyCreatedAsset = Asset.objects.create(userProfile = currentUser, assetName = asset, timeBought = datetime.now(), shares = shares, priceBought = currentPrice)
                        currentBalance.shares -= totalBuy
                        currentBalance.save()
                return redirect('home')
            else:
                error = "Must buy 1 or more shares"
    selectedAsset = request.GET.get('asset')
    method = request.GET.get('BorS')
    currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + selectedAsset + '/quote?displayPercent=true')
    jsonData = json.loads(currentSearch.content)
        
    if (not jsonData['primaryExchange'] == 'crypto'):
        stockReq = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + selectedAsset + '/chart/1m').content
        stockChartData = json.loads(stockReq)
        for pos, obj in enumerate(stockChartData):
            date = obj.pop('label', None)
            close = float(obj.pop('close', None))
            data = {u'label': date, u'close': close, u'pos': int(pos)}
            stockChartData[pos] = data
        graphic = getGraph(request, stockChartData).content
        return render(request, 'XChange/assetDetails.html', {'selectedAsset': jsonData, 'graphic': graphic, 'currentBalance': currentBalanceAmount, 'method': method})
    return render(request, 'XChange/assetDetails.html', {'selectedAsset': jsonData, 'currentBalance': currentBalanceAmount, 'method': method, 'error': error})
    
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
    currentProfile = UserProfile.objects.get(user = request.user)
    
    if (request.method == 'POST'):
        if (request.POST.get('submit') == 'Logout'):
            logout(request)
            return render(request, 'XChange/index.html')
    userAssets = Asset.objects.filter(userProfile = currentProfile).exclude(assetName = 'USD')
    totalValues = []
    assetNames = []
    for x in userAssets:
        try:
            currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + str(x.assetName).strip() + '/quote')
        except requests.exceptions.RequestException:
            pass
        jsonData = json.loads(currentSearch.content)
        totalValues.append(round(jsonData['latestPrice'] * x.shares, 2))
        assetNames.append(jsonData['companyName'])
        
    filteredUserAssets = []
    filteredTotalValues = []
    filteredAssetNames = []
        
    userAssetsList = list(userAssets)
    totalValuesList = totalValues
    i = 0
    while(i < userAssets.count()):
        if (i > 5):
            break
        max = 0
        for pos, x in enumerate(userAssetsList):
            if totalValues[pos] > max:
                max = totalValues[pos]
        index = totalValues.index(max)
        filteredUserAssets.append(userAssetsList[index])
        filteredTotalValues.append(totalValues[index])
        filteredAssetNames.append(assetNames[index])
        
        del userAssetsList[index]
        del totalValues[index]
        del assetNames[index]
        i = i + 1
            
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
        
    graphic = getHomeGraph(request, userAssets).content
    filteredUserAssets = zip(filteredUserAssets, filteredTotalValues, filteredAssetNames)
    return render(request, 'XChange/home.html', {'userAssets': filteredUserAssets, 'graphic': graphic, 'cryptoTop': cryptoTop, 'stockMovers': stockMovers})
    
def myPortfolio(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (djSettings.LOGIN_URL, request.path))
    graphic = None
    currentProfile = UserProfile.objects.get(user = request.user)
    userAssets = Asset.objects.filter(userProfile = currentProfile)
    userBookmarks = Bookmark.objects.filter(userProfile = currentProfile).distinct()
    currentBalance = userAssets.get(assetName = 'USD')
    currentBalance = round(currentBalance.shares * currentBalance.priceBought, 2)
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
                
            selectedAsset = Asset.objects.get(userProfile = currentProfile, assetName = request.POST['assetGraph'])    
            if ('USD' not in selectedAsset.assetName):
                graphic = getGraph(request, stockChartData).content
            
            else: 
                graphic = None
            
            # selectedAsset = Asset.objects.get(userProfile = currentProfile, assetName = request.POST['assetGraph'])
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
    if(data[0]['close'] > data[-1]['close']):
        ax.plot(xPlots, yPlots, 'r', linewidth= 3)
    else:   
        ax.plot(xPlots, yPlots, 'g', linewidth= 3)
    ax.set_xticks(np.arange(min(xPlots),max(xPlots)+1, 1.0))
    
    ax.set_xticklabels(xTicks, rotation='vertical', fontsize=10)

    ax.set_xlabel('Day')
    ax.set_ylabel('Price')
    

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent = True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    # Send buffer in a http response the the browser with the mime type image/png set
    return HttpResponse(graphic, content_type="image/png")
    
def getHomeGraph(request, data):
    labels = []
    sizes = []
    latestPrices = []
    totalValue = 0
    
    for x in data:
        try:
            currentSearch = requests.get(djSettings.DATA_ENDPOINT + '/stock/' + str(x.assetName).strip() + '/quote')
        except requests.exceptions.RequestException:
            return None
        jsonData = json.loads(currentSearch.content)
        latestPrices.append(jsonData['latestPrice'])
        labels.append(x.assetName)
        totalValue = totalValue + round((x.shares * latestPrices[-1]), 2)
    
    for pos, x in enumerate(data):
        sizes.append(round((x.shares * latestPrices[pos])/totalValue*100, 2))
    arr = np.arange(100).reshape((10,10))
    fig = plt.figure(figsize=(7,6))
    ax1 = fig.add_subplot(111, frameon=False)
    for pos, x in enumerate(labels):
        labels[pos] = x + ' - ' + str(sizes[pos]) + '%'
    ax1.pie(sizes, startangle=90, labeldistance = 2)
    ax1.legend(labels, bbox_to_anchor=(1, 1.), loc = 'best', fancybox=True, framealpha=0)
    ax1.axis('equal')
    ax1.set_title("Total Portfolio Value: $" + str(totalValue), fontdict={'fontsize': 18, 'fontweight': 'medium'}, fontname='sans-serif' )
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent = True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    # Send buffer in a http response the the browser with the mime type image/png set
    return HttpResponse(graphic, content_type="image/png")