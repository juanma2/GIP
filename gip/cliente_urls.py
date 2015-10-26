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
from gip import views_cliente
from gip import views_proveedor

##All this urls are beyond /cliente/ :)
urlpatterns = [
    url(r'^$', views_cliente.index_cliente, name='index_cliente'),
    url(r'^productos/$', views_cliente.productos_cliente, name='productos_cliente'),
    url(r'^listas/$', views_cliente.listas_cliente, name='listas_cliente'),
    url(r'^listas/add/(?P<user_id>[0-9]+)$', views_cliente.listas_add_cliente, name='listas_add_cliente'),
    url(r'^listas/del/(?P<user_id>[0-9]+)$', views_cliente.listas_del_cliente, name='listas_del_cliente'),
    url(r'^add_tolist/(?P<lista_id>[0-9]+)/(?P<producto_id>[0-9]+)$', views_cliente.add_tolist, name='add_tolist'),
    url(r'^elemento/add/(?P<lista_id>[0-9]+)$', views_cliente.elemento_add_cliente, name='elemento_add_cliente'),
]
