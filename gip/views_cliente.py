import json
from collections import Counter

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

#import only the needed ones
from gip.models import *
from gip.utils import is_cliente
from gip.helper_pedidos import send_order

from django.db.models import Q

from django.shortcuts import redirect


ELEMENTOS_POR_PAGINA = 6

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def index_cliente(request):
    #we will retrieve Promo and show per Tarifa/User
    current_user = request.user
    username = str(current_user.username)
    current_page = "Inicio"
    promo_list = []
    #get user tarifa
    tarifas = Cliente.objects.filter(user_id=current_user.id).values('tarifa')
    for tarifa in tarifas:
      promo_to_add = Promo.objects.filter(tarifa=tarifa['tarifa'])
      if promo_to_add:
        for promo in promo_to_add:
         if promo.producto:
           promo_list.append(promo)
           #we should generate and add html of the product itself
         else:
           #we shoul send the html of the promo
           promo_list.append(promo) 
    #get tarifa:
    #Promo.objects.filter(tarifa=1)
    user_listas = Cliente.objects.get(id=current_user.id).listas.all()

    context = {'username': username, 
               'current_page': current_page,
               'user_listas': user_listas,
               'promo_list': promo_list}
    return render(request, 'cliente/index_cliente.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def productos_cliente(request):
    #we will retrieve Promo and show per Tarifa/User
    current_user = request.user
    username = str(current_user.username)
    current_page = "Productos"
    #get all the categories
    categorias_list = Categoria.objects.all()
    sub_categorias_list = []
    #TODO:filter using disable and filtering by tarifa my friend
    search_parameters = request.POST.copy()
    print search_parameters
    if search_parameters:
      #wipe out the csrf:
      search_parameters.pop('csrfmiddlewaretoken')
      #THE PAGINATION DO NOT WORK
      full_search = Q()
      if 'search' in search_parameters:
        #Miss split words and do it smart
        search_string=Q(nombre__icontains=search_parameters['search']) |  Q(descripcion__icontains=search_parameters['search'])# ' %(search_parameters['search'],search_parameters['search'])
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
      all_product_list = Producto.objects.filter(full_search)
      paginator = Paginator(all_product_list, ELEMENTOS_POR_PAGINA)
      if 'page' in search_parameters:
        page = search_parameters['page']
      else:
        page = 1
    else:
      all_product_list = Producto.objects.all()
      #this is he default search
      paginator = Paginator(all_product_list, ELEMENTOS_POR_PAGINA)
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
    user_listas = Cliente.objects.get(id=current_user.id).listas.all()
    context = {'username': username,
               'current_page': current_page,
               'product_list': product_list,
               'categorias_list': categorias_list,
               'sub_categorias_list': sub_categorias_list,
               'user_listas': user_listas,
               'search_parameters': search_parameters
		}
               
    return render(request, 'cliente/productos_cliente.html', context)



@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def listas_cliente(request):
    current_user = request.user
    username = str(current_user.username)
    current_page = "Listas"
    user_listas = Cliente.objects.get(id=current_user.id).listas.all()
    form_parameters = request.POST.copy()
    print form_parameters
    if form_parameters:
      print "something comes up!"
    print user_listas
    ##TODO: decide if should be all the lists retrieved here or Ajax
    full_listas = {}
    for lista_i in user_listas:
      full_listas[lista_i]= Elemento.objects.filter(lista_id = lista_i.id)

      #retrieve listas here, you should check the query generated by ORM and check indexes 
    print type(full_listas)

    context = {'username': username,
               'current_user': current_user,
               'current_page': current_page,
               'user_listas': user_listas,
               'full_listas': full_listas,
                }

    return render(request, 'cliente/listas_cliente.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def listas_add_cliente(request,user_id):
  search_parameters = request.POST.copy()
  print search_parameters
  my_cli = Cliente.objects.get(id=user_id)
  #TODO: Fix this.do not know why, but hitting "intro" send a different parameter
  if 'lista_to_add' in search_parameters:
    lis = Lista(nombre=search_parameters['lista_to_add'])
  elif 'lista' in search_parameters:
    lis = Lista(nombre=search_parameters['lista'])
  lis.save()
  my_cli.listas.add(lis.id)
  # Always return an HttpResponseRedirect after successfully dealing
  # with POST data. This prevents data from being posted twice if a
  # user hits the Back button.
  return HttpResponseRedirect(reverse('listas_cliente'))


@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def listas_del_cliente(request,user_id):
  #TODO: nothing check that this belong to the cliente
  search_parameters = request.POST.copy()
  my_cli = Cliente.objects.get(id=user_id)
  lis = Lista(id=search_parameters['lista_to_del'])
  lis.delete()
  #my_cli.listas.add(lis.id)
  # Always return an HttpResponseRedirect after successfully dealing
  # with POST data. This prevents data from being posted twice if a
  # user hits the Back button.
  return HttpResponseRedirect(reverse('listas_cliente'))

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def listas_update_cliente(request):
  try:
    #TODO: nothing check that this belong to the cliente
    search_parameters = request.POST.copy()
    print search_parameters
    lis = Lista(id=search_parameters['id'])
    lis.nombre = search_parameters['lista_to_update']
    lis.save()
    # my_cli.listas.add(lis.id)
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponse(lis.nombre, content_type="application/json")
  except:
    #I think that this will not work as I expected. TODO: Test it.
    return HttpResponseRedirect(reverse('listas_cliente'))


@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def lista_add_custom(request):
  current_user = request.user
  search_parameters = request.POST.copy()
  print search_parameters
  if request.is_ajax():
    user_listas = Cliente.objects.get(id=current_user.id).listas.all().values_list('id',flat=True)
    list_id = search_parameters['id'].split('_')[2]
    if int(list_id) in user_listas: #conditions..., we are in the right list
      #add the element here
      ele = Elemento(nombre=search_parameters['custom_to_add'],cantidad= 0, lista_id = list_id )
      ele.save()
      #TODO: check if the same name of elemento already exist
      data = {
        'msg':'0',
        '0':'reload',
        'name':search_parameters['custom_to_add'],
        'id': ele.id
      }
    else:
      data = {
        'msg':'1' ,
        '1':'reset'
      }

    pay_load = json.dumps(data)
    return HttpResponse(pay_load, content_type="application/json")
  else:
    return HttpResponseRedirect(reverse('lista_add_custom'))


@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def add_tolist(request,lista_id,producto_id):
  current_user = request.user
  #the session user is;
  print "the user"+str(current_user.id)
  print "want to add the product"+str(producto_id)+" to the list "+str(lista_id)
  #check if exist
  if request.is_ajax():
    if len(Elemento.objects.filter(producto_id = producto_id,lista_id = lista_id)) == 0:
      p = Producto.objects.get(id=producto_id)
      #AQUI!! estoy intentando guardar un elemento nuevo
      e = Elemento(nombre=p.nombre , cantidad= 0, producto_id = p.id, lista_id= lista_id )
      e.save()
      print e.id
      data = {
        'msg':'Producto incluido!!' , 
        '0':'reload'
      }
    else:
      data = {
        'msg':'el producto ya existe' ,
        '1':'reset'
      }
    pay_load = json.dumps(data)
    return HttpResponse(pay_load, content_type="application/json")
  else: 
    return HttpResponseRedirect(reverse('productos_cliente'))

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def del_fromlist(request,lista_id,elemento_id):
  current_user = request.user
  #the session user is;
  #print "the user"+str(current_user.id)
  #print "want to del the product"+str(elemento_id)+" of the list "+str(lista_id)
  #check if exist
  if request.is_ajax():
    #check that the element belong to the list
    if len(Elemento.objects.filter(id = elemento_id,lista_id = lista_id)) == 1:
     user_listas = Cliente.objects.get(id=current_user.id).listas.all().values_list('id',flat=True)
     #print user_listas
     #print lista_id
     #check that the user own the list
     if int(lista_id) in user_listas:
       #print "the user has this list"
       e = Elemento(id = elemento_id)
       e.delete()
       #print e.id
       data = {
         'msg':'Producto eliminado!!' ,
         '0':'reload',
         'lista_id': lista_id,
         'elemento_id': elemento_id ,
       }
     else:
       #dammm try catch!!
       data = {
         'msg':'el producto ya existe' ,
         '1':'reset'
       }

    else:
      data = {
        'msg':'el producto ya existe' ,
        '1':'reset'
      }
    pay_load = json.dumps(data)
    return HttpResponse(pay_load, content_type="application/json")
  else:
    return HttpResponseRedirect(reverse('productos_cliente'))


#Todo: Would be nice if this request is ajax and is not properly prroceessed (302, redirect the whole page, no the div))
@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def element_update_list(request):
  print "want to update an element"
  try:
    search_parameters = request.POST.copy()
    #sadly, I can only send the id... that has the format: elem_LISTID_ELEMID
    print search_parameters
    lista_id = search_parameters['id'].split('_')[1]
    elem_id = search_parameters['id'].split('_')[2]
    paramenter_sort = search_parameters['id'].split('_')[0]
    print "we are looking for elem  {0}  in list {1} and parameter {2} ".format(elem_id,lista_id,paramenter_sort)
    #we should check that this belongs to the user
    current_user = request.user
    ele = Elemento.objects.get(id = elem_id ,lista_id = lista_id)
    # TODO: check if the list belongs to the user
    # TODO: this, will need to be updated to cantidad_to_update or precio_to_update
    if search_parameters['id'].split('_')[0] == 'elem':
      ele.cantidad = search_parameters['elem_to_update']
      ele.save()
      data = {
        'msg': search_parameters['elem_to_update'],
        '0':'OK'
      }
    elif search_parameters['id'].split('_')[0] == 'stoc':
      ele.stock_optimo = search_parameters['elem_to_update']
      ele.save()
      data = {
        'msg': search_parameters['elem_to_update'],
        '0':'OK'
      }
    elif search_parameters['id'].split('_')[0] == 'exis':
      ele.existencias = search_parameters['elem_to_update']
      ele.save()
      data = {
        'msg': search_parameters['elem_to_update'],
        '0':'OK'
      }

    pay_load = json.dumps(data)
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponse(pay_load, content_type="application/json")
  except:
    data = {
      'msg': 'ERR!!!',
      '1':'ERROR'
    }
    pay_load = json.dumps(data)
    #I think that this will not work as I expected. TODO: Test it.
    return HttpResponse(pay_load, content_type="application/json")
    #return HttpResponseRedirect(reverse('listas_cliente'))


@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def pedidos(request):
    current_user = request.user
    username = str(current_user.username)
    current_page = "Pedidos"
    user_listas = Cliente.objects.get(id=current_user.id).listas.all()
    #sort by lista.. and add the staff there 
    full_listas = {}
    lista_compra = {}
    #Split products and elements.
    for lista_i in user_listas:
      #TODO: I am sure this can be done better, one query and split in code or... something like that
      full_listas[lista_i]= Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = False)
      lista_compra[lista_i]= Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = True)
    #remove elementos from listas, and create an independent one for the view
    #for i in full_listas:
    #  for k in full_listas[i]:
    #    if k.producto:
    #      full_listas_total[i] += k.cantidad * k.producto.precio
    context = {'username': username,
               'current_page': current_page,
               'user_listas': user_listas,
               'full_listas': full_listas,
               'lista_compra': lista_compra}
    return render(request, 'cliente/pedidos_cliente.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def make_pedido(request):
    print "we are in Make Pedidos"
    current_user = request.user
    cliente = Cliente.objects.get(user = current_user.id)
    username = str(current_user.username)
    user_listas = Cliente.objects.get(id=current_user.id).listas.all()
    cliente = Cliente.objects.filter(user = current_user.id)
    pedido = {}
    cliente = cliente.values()[0]
    orden = {}
    descripcion = {}
    precio = {}
    for lista_i in user_listas:
      current_list = Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = False)
      for ele in current_list:
        descripcion[ele.producto.product_ref] = ele.producto.nombre
        precio[ele.producto.product_ref] = float(ele.producto.precio)
        if ele.producto.product_ref in orden:
          orden[ele.producto.product_ref] += ele.cantidad
        else:
          orden[ele.producto.product_ref] = ele.cantidad
        ##yes.. I am accessing by ID to a dict...
        ##create Pedido like 
        ## pedido[0] will have the information related with the user
        ## pedido[0] = {'user_name':'CLIENTE1','date':'pick a standard','tarifa':'proveedor1'}....
        ## pedido[1] will have amounts and prices (should be enough, because the price belongs to the ref, no to any other thing
        ## pedido[1] = {'product_ref':'cantidad','CAJUL':'25','MNB':'34'} ....
        ## pedido[2] If more information is requested could do like:
        ## pedido[2] = {'product_ref':'whatever you need here, like comments','CAJUL':'comment',
    pedido['cliente'] = cliente
    pedido['orden'] = orden
    #we can send the price of the elements right now... not sure if is right
    pedido['precio'] = precio
    pedido['descripcion'] = descripcion
    print "Add logic to send order here"
    send_order(pedido)
    print "Update to pending to send or something like that"
    print "now, clean the remaining cantidades..."
    for lista_i in user_listas:
      current_list = Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = False).update(cantidad=0)
      current_list = Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = False).update(cantidad=1)
    #TODO: handle the exceptions!!
    return redirect('/cliente/historico/', request)




@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def historico(request):
    current_user = request.user
    username = str(current_user.username)
    current_page = "Historico"
    pedidos = Pedidos.objects.filter(cliente=current_user.id)
    #sort by lista.. and add the staff there 
    context = {'username': username,
               'current_page': current_page,
               'pedidos': pedidos,
               }
    return render(request, 'cliente/historico_pedidos.html', context)

