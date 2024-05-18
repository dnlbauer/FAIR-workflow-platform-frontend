"""
URL configuration for cwr_frontend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, re_path
from django.conf import settings
from revproxy.views import ProxyView

from cwr_frontend.views.DatasetListView import DatasetListView
from cwr_frontend.views.DatasetDetailView import DatasetDetailView

urlpatterns = [
    # list of datasets
    path('', DatasetListView.as_view(), name="dataset_list"),
    # regex for dataset ids with forward slash (id=prefix/object_id)
    re_path(r'dataset/(?P<id>[a-z0-9\/]+)', DatasetDetailView.as_view(), name="dataset_detail"),
    # proxy all api requests to cordra
    re_path(r'api/(?P<path>.*)', ProxyView.as_view(upstream=settings.CORDRA["URL"]), name="api"),
]
