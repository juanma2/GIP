"""gip URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from gip import views_proveedor

##All this urls are beyond /proveedor/ :)
urlpatterns = [
    url(r'^$', views_proveedor.index_proveedor, name='index_proveedor'),
    url(r'^productos/$', views_proveedor.productos_proveedor, name='productos_proveedor'),
    url(r'^(?P<proveedor_id>[0-9]+)/producto/(?P<producto_id>[0-9]+)/$', views_proveedor.edit_producto_proveedor, name='edit_producto_proveedor'),
    url(r'^(?P<proveedor_id>[0-9]+)/add_producto/$', views_proveedor.add_producto_proveedor, name='add_producto_proveedor'),
]
