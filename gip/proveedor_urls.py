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
    url(r'^(?P<proveedor_id>[0-9]+)/act_masive/$', views_proveedor.masive_add_producto_proveedor, name='masive_add_producto_proveedor'),
    url(r'^del_product/(?P<proveedor_id>[0-9]+)/(?P<product_id>[0-9]+)$', views_proveedor.del_product, name='del_product'),
    url(r'^clientes/$', views_proveedor.clientes_proveedor, name='clientes_proveedor'),
    url(r'^(?P<proveedor_id>[0-9]+)/add_cliente/$', views_proveedor.add_cliente_proveedor, name='add_cliente_proveedor'),
    url(r'^(?P<proveedor_id>[0-9]+)/edit_cliente/(?P<client_id>[0-9]+)/$', views_proveedor.edit_cliente_proveedor, name='edit_cliente_proveedor'),
    url(r'^(?P<proveedor_id>[0-9]+)/baja_cliente/(?P<client_id>[0-9]+)/$', views_proveedor.baja_cliente_proveedor, name='baja_cliente_proveedor'),
    url(r'^(?P<proveedor_id>[0-9]+)/masive_client/$', views_proveedor.masive_add_cliente_proveedor, name='masive_add_cliente_proveedor'),
    url(r'^(?P<proveedor_id>[0-9]+)/pedidos_estados/(?P<tab_str>\w+)/$', views_proveedor.get_tab_content, name='get_tab_content'),
    url(r'^(?P<proveedor_id>[0-9]+)/estado/(?P<pedido_id>[0-9]+)/(?P<transition>\w+)/$', views_proveedor.update_pedidostate, name='updte_pedidostate'),
    url(r'^(?P<proveedor_id>[0-9]+)/pedido/(?P<pedido_id>[0-9]+)/$', views_proveedor.get_pedido_content, name='get_pedido_content'),

    url(r'^pedidos/$', views_proveedor.pedidos_proveedor, name='pedidos_proveedor'),
]
