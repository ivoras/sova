"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from sova import views

urlpatterns = [
    url(r'^accept/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.accept, name='accept'),
    url(r'^unaccept/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.unaccept, name='unaccept'),
    url(r'^confirm/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.confirm, name='confirm'),
    url(r'^exitpoll/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.exitpoll, name='exitpoll'),
    url(r'^exitpollsave/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.exitpollsave, name='exitpollsave'),
    url(r'^saveuserprofile/(?P<token>[A-Za-z0-9=\-_]+)$', views.save_user_profile, name='saveuserprofile'),
    url(r'^edituserprofile/(?P<token>[A-Za-z0-9=\-_]+)$', views.edit_user_profile, name='edituserprofile'),
    url(r'^sendprofiletoken/$', views.send_profile_token, name='sendprofiletoken'),
    url(r'^getprofiletoken/(?P<person>[0-9]+)$', views.get_profile_token, name='getprofiletoken'),
    url(r'^getprofiletoken/$', views.get_profile_token, name='getprofiletoken'),
    url(r'^vote/(?P<event>[0-9]+)/(?P<person>[0-9]+)$', views.vote, name='vote'),
    url(r'^join/(?P<event>[0-9]+)/(?P<person>[0-9]+)$', views.join, name='join'),
    url(r'^unsubscribe/(?P<person>[0-9]+)$', views.unsubscribe, name='unsubscribe'),
    url(r'^unsubscribesave/(?P<person>[0-9]+)$', views.unsubscribesave, name='unsubscribesave'),
    url(r'^subscribe$', views.subscribe, name='subscribe'),
    url(r'^subscribesave$', views.subscribesave, name='subscribesave'),
    url(r'^subscribeconfirm$', views.subscribeconfirm, name='subscribeconfirm'),
    url(r'^contact$', views.contact, name='contact'),


    url(r'^login$',     views.vlogin,   name='login'),
    url(r'^logout$',    views.vlogout,  name='logout'),
    url(r'^about$',     views.about,    name='about'),
    url(r'^newevent$',  views.newevent, name='newevent'),
    url(r'^$',          views.index,    name='index'),
]
