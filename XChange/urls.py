from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login, name='login'),
    url(r'^settings', views.settings, name='settings'),
    url(r'^search', views.search, name='search'),
    url(r'^bookmarks', views.bookmarks, name='bookmarks'),
    url(r'^home', views.home, name='home'),
    url(r'^myPortfolio', views.myPortfolio, name='myPortfolio'),
]