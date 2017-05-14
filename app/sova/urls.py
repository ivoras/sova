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
    url(r'^saveuserprofile/(?P<token>[A-Za-z0-9=\-_]+)$', views.save_user_profile, name='saveuserprofile'),
    url(r'^edituserprofile/(?P<token>[A-Za-z0-9=\-_]+)$', views.edit_user_profile, name='edituserprofile'),
    url(r'^sendprofiletoken/$', views.send_profile_token, name='sendprofiletoken'),
    url(r'^getprofiletoken/(?P<person>[0-9]+)$', views.get_profile_token, name='getprofiletoken'),
    url(r'^getprofiletoken/$', views.get_profile_token, name='getprofiletoken'),
    url(r'^accept/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.accept, name='accept'),
    url(r'^unaccept/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.unaccept, name='unaccept'),
    url(r'^confirm/(?P<schedule>[0-9]+)/(?P<person>[0-9]+)$', views.confirm, name='confirm'),
    url(r'^vote/(?P<event>[0-9]+)/(?P<person>[0-9]+)$', views.vote, name='vote'),
    url(r'^join/(?P<event>[0-9]+)/(?P<person>[0-9]+)$', views.join, name='join'),
    url(r'^$', views.index, name='index'),

]
