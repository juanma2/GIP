from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import redirect

from gip.models import Producto

import sys, time






#import only the needed ones
from gip.models import *

from gip.utils import is_proveedor

ELEMENTOS_POR_PAGINA_PROVEEDOR = 20
PROVEEDOR_ATTRIBUTE = 'proveedor'

@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def index_proveedor(request):
  my_test_string = 'Vista Proveedor'
  context = {'my_test_string': my_test_string}
  return render(request, 'proveedor/index_proveedor.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def productos_proveedor(request):
  #we will retrieve Promo and show per Tarifa/User
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  print proveedor.id
  print proveedor
  #get all the categories
  categorias_list = Categoria.objects.all()
  sub_categorias_list = []
  #TODO:filter using disable and filtering by tarifa my friend
  search_parameters = request.POST.copy()
  print search_parameters
  if search_parameters:
    #wipe out the csrf:
    search_parameters.pop('csrfmiddlewaretoken')
    full_search = Q()
    #if we are searching, we are searching one proveedor
    proveedor_search = (Q(proveedor = proveedor.id))
    if 'search' in search_parameters:
      print "a provider is searching!!"
      #Miss split words and do it smart
      search_string= Q(nombre__icontains=search_parameters['search']) |  Q(descripcion__icontains=search_parameters['search']) | Q(product_ref__icontains=search_parameters['search']) # ' %(search_parameters['search'],search_parameters['search'])
      full_search = full_search & search_string
    if 'categoria' in search_parameters:
      cat_id = int(search_parameters['categoria'].split('_')[1])
      search_cat = Q(categoria__id=cat_id)
      full_search = full_search & search_cat
    if 'subcategoria' in search_parameters:
      #TODO:is not tested, Will be necessary look for the father first, or check in the models :/
      subcat_id = Categoria.objects.get(nombre=search_parameters['subcategoria']).id
      search_subcat = Q(categoria__id=Categoria.objects.get(nombre=search_parameters['categoria']).id)
      full_search = full_search & search_subcat
    #add the provider here
    full_search = full_search & proveedor_search
    all_product_list = Producto.objects.filter(full_search).order_by('-id')
    paginator = Paginator(all_product_list, ELEMENTOS_POR_PAGINA_PROVEEDOR)
    if 'page' in search_parameters:
      page = search_parameters['page']
    else:
      page = 1
  else:
    all_product_list = Producto.objects.filter(proveedor= proveedor.id).order_by('-id')
    #this is he default search
    paginator = Paginator(all_product_list, ELEMENTOS_POR_PAGINA_PROVEEDOR)
    try:
      page = request.GET.get('page')
    except:
      #not sure
      page =  1
  try:
      product_list = paginator.page(page)
  except PageNotAnInteger:
      # If page is not an integer, deliver first page.
      product_list = paginator.page(1)
  except EmptyPage:
      # If page is out of range (e.g. 9999), deliver last page of results.
      product_list = paginator.page(paginator.num_pages)
  #Get the listas 
  context = {'username': username,
             'current_page': current_page,
             'proveedor': proveedor,
             'product_list': product_list,
             'categorias_list': categorias_list,
             'sub_categorias_list': sub_categorias_list,
             'search_parameters': search_parameters
              }

  return render(request, 'proveedor/productos_bootstrap_proveedor.html', context)


@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def edit_producto_proveedor(request, proveedor_id, producto_id):
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  categorias_list = Categoria.objects.all()
  ##Check if the proveedor is the right one... avoid requests from another providers
  if str(proveedor.id) == proveedor_id:
    producto = Producto.objects.get(id=producto_id)
    edit_producto = Producto.objects.filter(product_ref=producto.product_ref)
    tarifas_availables = Tarifas.objects.filter(elproveedor=proveedor.id)
    ##We have something to save ....
    edit_parameters = request.POST.copy()
    if edit_parameters:
      edit_parameters.pop('csrfmiddlewaretoken')
      p = Producto.objects.get(id=producto_id)
      print edit_parameters
      p.cantidad_minima = edit_parameters['cantidad_minima']
      p.categoria_id = edit_parameters['categoria']
      p.product_ref = edit_parameters['product_ref']
      p.formato = edit_parameters['formato']
      p.descripcion = edit_parameters['texcontenido']
      p.nombre = edit_parameters['nombre']
      current_tarifa = 'tarifa_'+str(p.tarifa_id)
      if edit_parameters[current_tarifa] and edit_parameters[current_tarifa] != [u'']:
        p.precio = edit_parameters[current_tarifa]
        edit_parameters.pop(current_tarifa)
      p.save()
      for i in tarifas_availables:
        current_tarifa = 'tarifa_'+str(i.id)
        if current_tarifa in edit_parameters:
          print "we want to update a tarifa"
          if edit_parameters[current_tarifa] != [u'']:
            print "and there is a value for "+ current_tarifa
            #we need to look and update this product, but we don't know which one is.. so.. load them all
            #Maybe the product does not exist
            #TODO: rethink this aprproach, looks weird
            try:
              producto_to_update = Producto.objects.get(product_ref=p.product_ref,tarifa_id=i.id)
              producto_to_update.precio = edit_parameters[current_tarifa]
              producto_to_update.save()
            except:
              #looks like the product does not exist
              new_product = Producto()
              new_product.cantidad_minima = edit_parameters['cantidad_minima']
              new_product.categoria_id = edit_parameters['categoria']
              new_product.product_ref = edit_parameters['product_ref']
              new_product.formato = edit_parameters['formato']
              new_product.descripcion = edit_parameters['texcontenido']
              new_product.nombre = edit_parameters['nombre']
              new_product.precio = edit_parameters[current_tarifa]
              new_product.tarifa_id = int(current_tarifa.split('_')[1])
              new_product.proveedor_id = p.proveedor_id
              new_product.save()
      #  redirect('/proveedor/404/', request)
      producto = p
  else:
    return redirect('/proveedor/404/', request)
  context= {'username': username,
             'current_page': current_page,
             'proveedor': proveedor,
             'producto': producto,
             'edit_producto': edit_producto,
             'tarifas_availables': tarifas_availables,
             'categorias_list': categorias_list,
              }

  return render(request, 'proveedor/edit_producto_bootstrap_proveedor.html', context)


@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def add_producto_proveedor(request, proveedor_id):
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  status_answer = {}
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  categorias_list = Categoria.objects.all()
  ##Check if the proveedor is the right one... avoid requests from another providers
  if str(proveedor.id) == proveedor_id:
    tarifas_availables = Tarifas.objects.filter(elproveedor=proveedor.id)
    ##We have something to save ....
    add_parameters = request.POST.copy()
    print add_parameters
    if add_parameters:
      add_parameters.pop('csrfmiddlewaretoken')
      exist = Producto.objects.filter(product_ref = add_parameters['product_ref'])
      if not exist:
        print "the product do not exist" 
        for i in tarifas_availables:
          if add_parameters['tarifa_'+str(i.id)]:
          #may happen that tarifa is empty..nothing will be created, and nothing will be returned, JS shuold help with this. and allow us to create products with only some tarifas and not all of them.
            try:
              print "we try to create this"
              p = Producto()
              add_parameters['cantidad_minima']
              p.cantidad_minima = add_parameters['cantidad_minima']
              p.categoria_id = add_parameters['categoria']
              p.product_ref = add_parameters['product_ref']
              p.formato = add_parameters['formato']
              p.descripcion = add_parameters['texcontenido']
              p.nombre = add_parameters['nombre']
              p.proveedor_id = proveedor.id
              #check tarifas and precios...
              p.tarifa_id = i.id
              p.precio = add_parameters['tarifa_'+str(i.id)]
              p.save()
              print "we have an id"
              print p.id
            except:
              print sys.exc_info()[0]
              status_answer['error'] = 'Error creating product'+str(time.time())
              print "Error!! this will never redirect properly... find a nice way, but.. the product came with missing information"
              return redirect('/proveedor/error_proveedor/', request)
      else:
        status_answer['exist'] = '/proveedor/'+proveedor_id+'/producto/'+str(exist[0].id)+'/'
      #endfor.. means that products was crearted correctly
      if 'edit' in add_parameters['create'] and not 'error' in status_answer:
        print "we should not have issues here..."
        print p.id
        return redirect('/proveedor/'+proveedor_id+'/producto/'+str(p.id),request)
    else:
      #first time here... or someone is trying something... there is no add_parameters :/
      pass 
  else:
    #someone is trying something... add logg to this, is looking for another proveedor
    return redirect('/proveedor/404/', request)
  context= { 'username': username,
             'current_page': current_page,
             'status_answer': status_answer,
             'proveedor': proveedor,
             'tarifas_availables': tarifas_availables,
             'categorias_list': categorias_list,
              }
  return render(request, 'proveedor/add_producto_bootstrap_proveedor.html', context)

