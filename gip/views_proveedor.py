from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models import Count
from django.shortcuts import redirect

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings


from gip.helper_proveedor import list_grouper, generator_pedidos_tabs, generator_pedido_content




from gip.models import Producto, Cliente

import sys, time
import datetime
import json
import ast






#import only the needed ones
from gip.models import *

from gip.utils import is_proveedor

##FFS add all this in one file settings??

ELEMENTOS_POR_PAGINA_PROVEEDOR = 20
ELEMENTOS_POR_PAGINA_CLIENTE = 5
PROVEEDOR_ATTRIBUTE = 'proveedor'
CLIENTE_ATTRIBUTE = 'cliente'

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
  tarifas_availables = Tarifas.objects.filter(elproveedor=proveedor.id).order_by('id')
  print search_parameters
  if search_parameters:
    #wipe out the csrf:
    search_parameters.pop('csrfmiddlewaretoken')
    full_search = Q()
    #we filer using only one tarifa...
    only_one_product = (Q(tarifa = tarifas_availables[0].id))
    full_search = full_search & only_one_product
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
    all_product_list = Producto.objects.filter(full_search).order_by('-fecha_actualizacion').exclude(baja=True)
    paginator = Paginator(all_product_list, ELEMENTOS_POR_PAGINA_PROVEEDOR)
    if 'page' in search_parameters:
      page = search_parameters['page']
    else:
      page = 1
  else:
    all_product_list = Producto.objects.filter(proveedor= proveedor.id, tarifa = tarifas_availables[0].id).order_by('-fecha_actualizacion').exclude(baja=True)
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
    edit_producto = Producto.objects.filter(product_ref=producto.product_ref,proveedor=proveedor.id)
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
      p.fecha_actualizacion = datetime.datetime.now()
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


@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def masive_add_producto_proveedor(request,proveedor_id):
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  status_answer = {}
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  categorias_list = Categoria.objects.all()
  ##Check if the proveedor is the right one... avoid requests from another providers
  ##TODO:Add a lot of logic... is not done!!
  context= { 'username': username,
             'current_page': current_page,
             'status_answer': status_answer,
             'proveedor': proveedor,
             'categorias_list': categorias_list,
              }
  return render(request, 'proveedor/masive_product_bootstrap_proveedor.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def del_product(request,proveedor_id,product_id):
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  print "requested product delete"
  print proveedor_id
  print product_id
  if str(proveedor.id) == proveedor_id:
    if request.is_ajax():
      current_product = Producto.objects.get(id = product_id)
      all_of_them = Producto.objects.filter(product_ref = current_product.product_ref)
      try:
        for i in all_of_them:
          i.baja = True
          i.save()
          i.id 
        data = {
           'msg':'Producto eliminado!!' ,
           '0':'reload',
         }
        print "Job done!!"
      except:
         #dammm try catch!!
         data = {
           'msg':'No ha sido posible realizar su peticin' ,
           '0':'reload'
         }
      pay_load = json.dumps(data)
      return HttpResponse(pay_load, content_type="application/json")
    else:
      return HttpResponseRedirect(reverse('productos_cliente'))
  else:
      return HttpResponseRedirect(reverse('nopnopnopnpo'))


@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def clientes_proveedor(request):
  current_user = request.user
  print current_user.id
  username = str(current_user.username)
  current_page = "Clientes"
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  print proveedor
  print "we do this search when arrive to the page"
  client_list = User.objects.filter(groups__id=proveedor.id).exclude(groups__name=PROVEEDOR_ATTRIBUTE).exclude(cliente__baja=True).order_by('-id')
  print client_list
  search_parameters = request.POST.copy()
  if search_parameters:
    print "there is a search"
    print search_parameters
    #wipe out the csrf:
    search_parameters.pop('csrfmiddlewaretoken')
    full_search = Q()
    #if we are searching, we are searching one proveedor
    proveedor_search = (Q(groups__id = proveedor.id))
    if 'search' in search_parameters:
      print "a provider is searching client!!"
      #Miss split words and do it smart
      search_string= Q(cliente__nombre__icontains=search_parameters['search']) |  Q(cliente__cif__icontains=search_parameters['search']) # ' %(search_parameters['search'],search_parameters['search'])
      full_search = full_search & search_string
    full_search = full_search & proveedor_search
    print full_search
    all_client_list = User.objects.filter(full_search).order_by('-id').exclude(groups__name=PROVEEDOR_ATTRIBUTE).exclude(cliente__baja=True)
    paginator = Paginator(all_client_list, ELEMENTOS_POR_PAGINA_CLIENTE)
    print "the result is"
    print all_client_list
    if 'page' in search_parameters:
      page = search_parameters['page']
    else:
      page = 1
  else:
    all_client_list = User.objects.filter(groups__id=proveedor.id).exclude(groups__name=PROVEEDOR_ATTRIBUTE).exclude(cliente__baja=True).order_by('-id')
    #this is he default search
    paginator = Paginator(all_client_list, ELEMENTOS_POR_PAGINA_CLIENTE)
    try:
      page = request.GET.get('page')
    except:
      #not sure
      page =  1
  try:
      client_list = paginator.page(page)
  except PageNotAnInteger:
      # If page is not an integer, deliver first page.
      client_list = paginator.page(1)
  except EmptyPage:
      # If page is out of range (e.g. 9999), deliver last page of results.
      client_list = paginator.page(paginator.num_pages)

  context= { 'username': username,
             'current_page': current_page,
             'proveedor': proveedor,
             'client_list': client_list,
              }
  return render(request, 'proveedor/clientes_bootstrap_proveedor.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def baja_cliente_proveedor(request,proveedor_id,client_id):
  current_user = request.user
  username = str(current_user.username)
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  client_list = User.objects.filter(groups__id=proveedor.id).exclude(groups__name=PROVEEDOR_ATTRIBUTE).order_by('-id')
  if request.is_ajax():
    #check that the element belong to the list
    client = Cliente.objects.get(id=client_id)
    if str(proveedor.id) == proveedor_id: 
      if client.baja == False:
        client.baja = True
        client.save()
        #print e.id
        data = {
          'msg':'cliente eliminado!!' ,
          '0':'reload'
        }
      else:
        #dammm try catch!!
        data = {
          'msg':'el cliente ya estaba dado de baja!!, si el error persiste ponte en contacto con nosotros' ,
          '1':'reset'
        }
      pay_load = json.dumps(data)
      return HttpResponse(pay_load, content_type="application/json")
    else:
      print "Someone is playing bad.. proabbly"+str(proveedor_id)
      return redirect('/proveedor/404/', request)
  else:
    return HttpResponseRedirect(reverse('cliente_proveedor'))



login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def add_cliente_proveedor(request, proveedor_id):
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  status_answer = {}
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  categorias_list = Categoria.objects.all()
  ##Check if the proveedor is the right one... avoid requests from another providers
  print "provider should match"
  print proveedor.id
  print proveedor_id
  if str(proveedor.id) == proveedor_id:
    tarifas_availables = Tarifas.objects.filter(elproveedor=proveedor.id)
    ##We have something to save ....
    add_parameters = request.POST.copy()
    print add_parameters
    if add_parameters:
      print add_parameters['cliente']
      #create user, add cliente group, add proveedor group, and add cliente object
      user = User.objects.create_user(add_parameters['cliente'], add_parameters['email'],add_parameters['password'])
      grupo_cliente = Group.objects.get(name='cliente')
      grupo_proveedor = Group.objects.get(id=proveedor.id)
      user.groups.add(grupo_cliente)
      user.groups.add(grupo_proveedor)
      user.save()
      print add_parameters['tarifa']
      client = Cliente(user = user, nombre = add_parameters['nombre'], descripcion = add_parameters['texcontenido'], cif = add_parameters['nif'], direccion = add_parameters['direccion'], ciudad = add_parameters['ciudad'], telefono = add_parameters['telefono'], contacto_nombre = add_parameters['nombre_contacto'] )
      #add tarifa ,listas(need to has at least one list), but check with no list), destinos de reparto
      client.save()
      client.tarifa.add(add_parameters['tarifa'].split('_')[1])
      #TODO:check the real cp ID , not the one the come with the request like 41011
      client.destino_reparto.add(1)
      lis = Lista(nombre='lista 1')
      lis.save()
      client.listas.add(lis.id)
      client.save()
      print "destino reparto is not properly added"
    else:
      #first time here... or someone is trying something... there is no add_parameters :/
      print "looks like something is missing or is the first visit"
      pass
  else:
    print "we should be redirected... this is not real provider"
    #someone is trying something... add logg to this, is looking for another proveedor
    return redirect('/proveedor/404/', request)
  context= { 'username': username,
             'current_page': current_page,
             'status_answer': status_answer,
             'proveedor': proveedor,
             'tarifas_availables': tarifas_availables,
             'categorias_list': categorias_list,
              }
  return render(request, 'proveedor/add_cliente_bootstrap_proveedor.html', context)

login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def edit_cliente_proveedor(request, proveedor_id, client_id):
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  status_answer = {}
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  categorias_list = Categoria.objects.all()
  ##Check if the proveedor is the right one... avoid requests from another providers
  print "provider should match"
  print proveedor.id
  print proveedor_id
  if str(proveedor.id) == proveedor_id:
    tarifas_availables = Tarifas.objects.filter(elproveedor=proveedor.id)
    client = Cliente.objects.get(id=client_id) 
    print "client data"
    print client
    print client_id
    print "destino reparto is not properly added"
    print client.contacto_nombre
    edit_parameters = request.POST.copy()
    if edit_parameters:
      tarifa_requested = Tarifas.objects.filter(elproveedor=proveedor.id,id = edit_parameters['tarifa'].split('_')[1])
      print tarifa_requested
      print "we are going to save it"
      print edit_parameters
      client.fax = edit_parameters['fax']
      client.nombre_envio = edit_parameters['nombre_envio']
      client.direccion_envio = edit_parameters['direccion_envio']
      client.fax_contacto = edit_parameters['fax_contacto']
      client.cif = edit_parameters['nif']
      client.descripcion = edit_parameters['texcontenido']
      client.contacto_ciudad = edit_parameters['ciudad_contacto']
      client.ciudad_envio = edit_parameters['ciudad_envio']
      client.ciudad = edit_parameters['ciudad']
      client.direccion_contacto = edit_parameters['direccion_contacto']
      client.texcontenido_envio = edit_parameters['texcontenido_envio']
      client.fax_envio = edit_parameters['fax_envio']
      client.cp = edit_parameters['cp']
      client.movil = edit_parameters['movil']
      #TODO: try catch a bit
      print "before tarifa"
      try:
        print "we have tarifa"
        client.tarifa.clear()
        client.tarifa.add( tarifa_requested[0].id)
        print "we did tarifa"
      except:
        pass
      client.cp_contacto = edit_parameters['cp_contacto']
      client.contacto_nombre = edit_parameters['nombre_contacto']
      client.email_contacto = edit_parameters['email_contacto']
      client.direccion = edit_parameters['direccion']
      client.texcontenido = edit_parameters['texcontenido']
      client.contacto_telefono = edit_parameters['telefono_contacto']
      client.telefono_envio = edit_parameters['telefono_envio']
      client.email_envio = edit_parameters['email_envio']
      client.movil_envio = edit_parameters['movil_envio']
      #client.cliente = edit_parameters['cliente']
      client.nombre = edit_parameters['nombre']
      client.telefono = edit_parameters['telefono']
      client.email = edit_parameters['email']
      client.contacto_movil = edit_parameters['movil_contacto']
      client.contacto_fax = edit_parameters['fax_contacto']
      client.save()
      ##IS MISSING PROVINCIA, CP 
      print edit_parameters
    else:
      #first time here... or someone is trying something... there is no add_parameters :/
      print "looks like something is missing or is the first time!"
      pass
  else:
    print "we should be redirected... this is not real provider"
    #someone is trying something... add logg to this, is looking for another proveedor
    return redirect('/proveedor/404/', request)
  context= { 'username': username,
             'current_page': current_page,
             'status_answer': status_answer,
             'proveedor': proveedor,
             'tarifas_availables': tarifas_availables,
             'categorias_list': categorias_list,
             'client': client,
           }
  return render(request, 'proveedor/edit_cliente_bootstrap_proveedor.html', context)


@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def masive_add_cliente_proveedor(request,proveedor_id):
  print "we are in the right place to ad masive clients"
  current_user = request.user
  username = str(current_user.username)
  current_page = "Productos"
  status_answer = {}
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  categorias_list = Categoria.objects.all()
  ##Check if the proveedor is the right one... avoid requests from another providers
  ##TODO:Add a lot of logic... is not done!!
  context= { 'username': username,
             'current_page': current_page,
             'status_answer': status_answer,
             'proveedor': proveedor,
             'categorias_list': categorias_list,
              }
  return render(request, 'proveedor/masive_client_bootstrap_proovedor.html', context)


@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def pedidos_proveedor(request):
  current_user = request.user
  print current_user.id
  username = str(current_user.username)
  current_page = "Clientes"
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  client_list = User.objects.filter(groups__id=proveedor.id).exclude(groups__name=PROVEEDOR_ATTRIBUTE).exclude(cliente__baja=True).order_by('-id')
  #Count all of them, TODO:check how expensive if this query and think about options, fix the format, kills me :/
  #even better, think in cache the numbers in other place.. is not so accurate, but woudl work
  list_pedidos = Pedidos.objects.filter(proveedor_id = proveedor.id)
  #is ugly, but should make jinja easier
  search_parameters = request.POST.copy()
  lista_pedidos , tabs = list_grouper(list_pedidos)
  print "lista_pedidos"
  print lista_pedidos
  #if search_parameters:
  context= { 'username': username,
             'current_page': current_page,
             'proveedor': proveedor,
             'tabs': tabs,
             'lista_pedidos' : lista_pedidos,
              }
  return render(request, 'proveedor/pedidos_clientes_bootstrap_proveedor.html', context)



@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def get_tab_content(request,proveedor_id,tab_str):
  #TODO: this is duplicated inside helpers_proveeedor, unify and add to settings
  #You cannot user characters like "-_" in here, cause you cannot afford ids MTF
  def_tabs = settings.DEF_TABS
  grouped_by = settings.GROUPED_BY
  current_user = request.user
  username = str(current_user.username)
  #how that can work iwth many providers??
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  if request.is_ajax():
    if str(proveedor.id) == proveedor_id:
      state_list = grouped_by[tab_str.replace('_',' ')]
      print "we have a proveedor"+proveedor_id
      print "we have some ids.."+str(state_list)
      pedidos_list = Pedidos.objects.filter(proveedor_id = proveedor.id,pedidostate__in=state_list)
      html = generator_pedidos_tabs(pedidos_list)
      #set a html string response (facepalm)
      return HttpResponse(html)
    else:
      print "Someone is playing bad.. proabbly"+str(proveedor_id)
      return redirect('/proveedor/404/', request)
  else:
    return HttpResponseRedirect(reverse('pedidos_proveedor'))

@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def ajax_tab_counters(request,proveedor_id):
  current_user = request.user
  print current_user.id
  username = str(current_user.username)
  def_tabs = settings.DEF_TABS
  grouped_by = settings.GROUPED_BY
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  html = ''
  if request.is_ajax():
    if str(proveedor.id) == proveedor_id:
      list_pedidos = Pedidos.objects.filter(proveedor_id = proveedor.id)
      #is ugly, but should make jinja easier
      lista_pedidos , tabs = list_grouper(list_pedidos)
      #counter_pedidos = Pedidos.objects.filter(proveedor_id = proveedor.id).values('pedidostate').annotate(total=Count('pedidostate'))
      print "lista_pedidos"
      print lista_pedidos
      print "tabs"
      print tabs
      for i in lista_pedidos:
        html += '<li class="{0}"><a href="#" onclick="gettab(\'{1}\')">'.format(i.replace(' ','-'), i.replace(' ','_') )
        html += i
        html += '<span class="badge">{0}</span>'.format(len(lista_pedidos[i]))
        html += ' </a></li>'
  print html 
  return HttpResponse(html)
 




@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def update_pedidostate(request,proveedor_id,pedido_id,transition):
  #TODO: this is duplicated inside helpers_proveeedor, unify and add to settings
  #You cannot user characters like "-_" in here, cause you cannot afford ids MTF
  def_tabs = settings.DEF_TABS
  grouped_by = settings.GROUPED_BY
  current_user = request.user
  username = str(current_user.username)
  #how that can work iwth many providers??
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  print "we have a proveedor"
  if request.is_ajax():
    if str(proveedor.id) == proveedor_id:
      print "we have a proveedor"+proveedor_id
      print "we want to move the pedido "+str(pedido_id)+ "using:"+str(transition)
      pedido = Pedidos.objects.get(id=pedido_id)
      #that is stupid, but works with, int, no with the str.. for reasons
      pedido.pedidostate = int(pedido.pedidostate)
      #till someone thinks in something better... this is like pedido.transition
      result = getattr(pedido,transition)()
      pedido.save()
      print "and the winner is:"
      print result
      #restul = getattr(pedido, 'bar')()
      data = {
          'msg': result,
          '1':'reset'
        }
      pay_load = json.dumps(data)
      return HttpResponse(pay_load, content_type="application/json")
    else:
      print "Someone is playing bad.. proabbly"+str(proveedor_id)
      return redirect('/proveedor/404/', request)
  else:
    return HttpResponseRedirect(reverse('pedidos_proveedor'))




@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def get_pedido_content(request,proveedor_id,pedido_id):
  #TODO: this is duplicated inside helpers_proveeedor, unify and add to settings
  #You cannot user characters like "-_" in here, cause you cannot afford ids MTF
  def_tabs = settings.DEF_TABS
  grouped_by = settings.GROUPED_BY
  current_user = request.user
  username = str(current_user.username)
  #how that can work iwth many providers??
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  if request.is_ajax():
    if str(proveedor.id) == proveedor_id:
      pedido = Pedidos.objects.get(id = pedido_id)
      html = generator_pedido_content(pedido)
      #set a html string response (facepalm)
      return HttpResponse(html)
    else:
      print "Someone is playing bad.. proabbly"+str(proveedor_id)
      return redirect('/proveedor/404/', request)
  else:
    return HttpResponseRedirect(reverse('pedidos_proveedor'))


@login_required(login_url='/mylogin/')
@user_passes_test(is_proveedor)
def retry_pedido(request,proveedor_id,pedido_id):
  current_user = request.user
  username = str(current_user.username)
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  print "requested proveedor"
  print proveedor_id
  msg = ''
  status = 0
  action = 'reload'
  if str(proveedor.id) == proveedor_id:
    if request.is_ajax():
      update_parameters = request.POST.copy()
      print update_parameters
      if update_parameters:
        pedido = Pedidos.objects.get(id= pedido_id)
        print "pedido to update"
        print pedido.id
        #this works only because order is not multiprovider
        cliente = pedido.cliente.all()[0]
        print "cliente  to update"
        print cliente.id 
        #here, should be enough a get.. if there is only one tarifa per pair cliente-proveedor
        tarifa = cliente.tarifa.filter(elproveedor = proveedor_id)[0]
        #the information comes like:
	# {u'DIS112_': [u''], u'DIS200_r1': [u'c1'], u'AJTH_': [u''], u'DIS171_r4': [u'c4']}
        #{OLDREF_NEWREF:[amount],}
        for i in update_parameters:
          print "one by one:"+str(i)
          if i.split('_')[1]:
            new_ref = i.split('_')[1]
            old_ref = i.split('_')[0] 
            print pedido.producto_serializado
            order = ast.literal_eval(pedido.producto_serializado)
            #disable the product
            print "diable old product from "+str(order['active'][old_ref])
            order['active'][old_ref] = 0 
            #we shuld look for the product
            try:
              producto = Producto.objects.get(product_ref = new_ref, tarifa__id = tarifa.id)
              order['descripcion'][new_ref]= producto.descripcion
              order['precio'][new_ref] = float(producto.precio)
              try:
                order['orden'][new_ref] = float(update_parameters[i])
              except:
                order['orden'][new_ref] = 1
              order['active'][new_ref] = 1
            except:
              msg += 'Parece que la refencia: '+new_ref+'  No existe asociada a la tarifa '+str(tarifa)+'\n'
        print "Our new order is ready:"
        print order
        if msg == '':
          #everything was fine...
          pedido.producto_serializado = order
          pedido.pedidostate= int(pedido.pedidostate)
          total = 0.0 
          for i in order['orden']:
            if order['active'][i] == 1:
              total += order['orden'][i]*order['precio'][i]
          pedido.total = total
          #we want to move to 12100, reformular pedido, we need to know the good transisition for this task
          for t in Pedidos.get_available_pedidostate_transitions(pedido):
            if t.target == 12100:
              result = getattr(pedido,t.name)()
          pedido.save()
          msg = 'Su propuesta ha sido tramitada'
          action = 'close'
          
    data = {
          'msg': msg,
          'action':action
    }
    print "Job done!!"
    pay_load = json.dumps(data)
    return HttpResponse(pay_load, content_type="application/json")
#      except:
#         #dammm try catch!!
#         data = {
#           'msg':'No ha sido posible realizar su peticin' ,
#           '0':'reload'
#         }
#      pay_load = json.dumps(data)
#      return HttpResponse(pay_load, content_type="application/json")
#    else:
#      return HttpResponseRedirect(reverse('productos_cliente'))
#  else:
#      return HttpResponseRedirect(reverse('nopnopnopnpo'))

