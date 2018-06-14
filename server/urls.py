"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from server.func import deploy
import web.views
import wx.views

urlpatterns = [
    path('', web.views.index),
    path('admin/', admin.site.urls),
    path('wx/', wx.views.wx),
    path('wx/token', wx.views.get_token),
    path('wx/responsechat', wx.views.get_replay_from_server),
    path('wx/registered', wx.views.registered),
    path('deploy/', deploy),
    path('whatismyip', web.views.whatismyip)
]
