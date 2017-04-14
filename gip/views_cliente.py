import json
import ast
from collections import Counter

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings


#import only the needed ones
from gip.models import *
from gip.utils import is_cliente
from gip.helper_pedidos import send_order, generate_modales_historico
from gip.helper_cliente import generate_modales_encurso

from django.db.models import Q

from django.shortcuts import redirect


ELEMENTOS_POR_PAGINA = 6
##FFS add all this in one file settings??
ELEMENTOS_POR_PAGINA_PROVEEDOR = 20
ELEMENTOS_POR_PAGINA_CLIENTE = 5
PROVEEDOR_ATTRIBUTE = 'proveedor'
CLIENTE_ATTRIBUTE = 'cliente'


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
    user_listas = Cliente.objects.get(user_id=current_user.id).listas.all()

    context = {'username': username, 
               'current_page': current_page,
               'user_listas': user_listas,
               'promo_list': promo_list}
    return render(request, 'cliente/index_r_cliente.html', context)

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
    cliente = Cliente.objects.filter(user_id = current_user.id)
    proveedor = cliente[0].user.groups.exclude(name=CLIENTE_ATTRIBUTE)[0]

    #TODO:filter using disable and filtering by tarifa my friend

    search_parameters = request.POST.copy()
    print search_parameters
    if search_parameters:
      #wipe out the csrf:
      search_parameters.pop('csrfmiddlewaretoken')
      full_search = Q( proveedor_id = proveedor.id)
      if 'search' in search_parameters:
        #Miss split words and do it smart
        search_string=Q(nombre__icontains=search_parameters['search']) |  Q(descripcion__icontains=search_parameters['search']) | Q(product_ref__icontains=search_parameters['search']) # ' %(search_parameters['search'],search_parameters['search'])
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
      all_product_list = Producto.objects.filter(proveedor_id = proveedor.id)
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
    user_listas = Cliente.objects.get(user_id=current_user.id).listas.all()
    context = {'username': username,
               'current_page': current_page,
               'product_list': product_list,
               'categorias_list': categorias_list,
               'sub_categorias_list': sub_categorias_list,
               'user_listas': user_listas,
               'search_parameters': search_parameters
		}
               
    return render(request, 'cliente/productos_r_cliente.html', context)



@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def listas_cliente(request):
    current_user = request.user
    username = str(current_user.username)
    current_page = "Listas"
    user_listas = Cliente.objects.get(user_id=current_user.id).listas.all()
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

    return render(request, 'cliente/listas_r_cliente.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def listas_add_cliente(request,user_id):
  search_parameters = request.POST.copy()
  print search_parameters
  my_cli = Cliente.objects.get(user_id=user_id)
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
  my_cli = Cliente.objects.get(user_id=user_id)
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
    user_listas = Cliente.objects.get(user_id=current_user.id).listas.all().values_list('id',flat=True)
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
        'id': ele.id,
        'table_id': list_id
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
     user_listas = Cliente.objects.get(user_id=current_user.id).listas.all().values_list('id',flat=True)
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
        'lista_id': lista_id ,
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
    user_listas = Cliente.objects.get(user_id=current_user.id).listas.all()
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
    return render(request, 'cliente/pedidos_r_cliente.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def make_pedido(request):
    print "we are in Make Pedidos"
    current_user = request.user
    cliente = Cliente.objects.get(user_id = current_user.id)
    username = str(current_user.username)
    user_listas = Cliente.objects.get(user_id=current_user.id).listas.all()
    #BUGGGGG!!!! TODO: nothing to say... 2 clients
    cliente = Cliente.objects.filter(user_id = current_user.id)
    print "we are going to use the cliente"
    print cliente
    print "with the user id:"
    print current_user.id
    proveedor = cliente[0].user.groups.exclude(name=CLIENTE_ATTRIBUTE)[0]
    pedido = {}
    cliente = cliente.values()[0]
    orden = {}
    descripcion = {}
    precio = {}
    active = {}
    #set for customs lists
    c_pedido, c_nombre, c_cantidad, c_lista, c_stock_optimo, c_existencias = {}, {}, {}, {}, {}, {}
    for lista_i in user_listas:
      current_list = Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = False)
      current_custom_list = Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = True)
      for ele in current_list:
        descripcion[ele.producto.product_ref] = ele.producto.nombre
        precio[ele.producto.product_ref] = float(ele.producto.precio)
        active[ele.producto.product_ref] = 1
        if ele.producto.product_ref in orden:
          orden[ele.producto.product_ref] += ele.cantidad
        else:
          orden[ele.producto.product_ref] = ele.cantidad
      #now, rise complexite twice, TODO: look into iterate twice over the same dict
      #this will save the custom lists
      for c_ele in current_custom_list:
        c_nombre[c_ele.id]= c_ele.nombre
        c_cantidad[c_ele.id]= c_ele.cantidad
        c_lista[c_ele.id]= c_ele.lista.id
        c_stock_optimo[c_ele.id]= c_ele.stock_optimo

    c_pedido['c_nombre'], c_pedido['c_cantitdad'], c_pedido['c_lista'], c_pedido['c_stock_optimo'] = c_nombre, c_cantidad, c_lista, c_stock_optimo
    pedido['cliente'] = cliente
    pedido['orden'] = orden
    #we can send the price of the elements right now... not sure if is right
    pedido['precio'] = precio
    pedido['descripcion'] = descripcion
    pedido['active'] = active 
    print "Add logic to send order here"
    #really?? again?? TODO: fix cliente
    cliente = Cliente.objects.get(user_id = current_user.id)
    try: 
      order_status = send_order(pedido,proveedor,c_pedido)
      print "the order_status is"
      print order_status
      if order_status is True: 
        for lista_i in user_listas:
          current_list = Elemento.objects.filter(lista_id = lista_i.id, producto_id__isnull = False).update(cantidad=0)
      return redirect('/cliente/historico/', request)
    #TODO: handle the exceptions!!
    except:
      #Something went wrong....
      print "something went wrong with the order"
      return redirect('/cliente/pedidos/',request)




@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def historico(request):
    current_user = request.user
    username = str(current_user.username)
    current_page = "Historico"
    #check how to improve the filter, this sounds like baaaad, is the flow definition wrong, I know.
    mis_estados = Q(pedidostate = '100') | Q (pedidostate = '12100') | Q(pedidostate = '10000')
    mis_estados = Q(pedidostate = '100') | Q (pedidostate = '12100') | Q(pedidostate = '10000' ) | Q(pedidostate = '20000')

    pedidos = Pedidos.objects.filter(cliente__user=current_user.id).exclude(mis_estados)
    pedidos_estados = {}
    #is ugly, but should make jinja easier
    print current_user.id
    for k in Pedidos.STATE_CHOICES:
      pedidos_estados[str(k[0])]=k[1] 
      #here we should decide which state will be an actual acction, like "Reformular Pedido":12100
    #sort by lista.. and add the staff there 
    pedidos_modales = generate_modales_historico(pedidos)
    context = {'username': username,
               'current_page': current_page,
               'pedidos': pedidos,
               'pedidos_modales': pedidos_modales,
               'pedidos_estados': pedidos_estados,
               }
    return render(request, 'cliente/historico_r_pedidos.html', context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def pedidos_en_curso(request):
    current_user = request.user
    username = str(current_user.username)
    current_page = "Curso"
    #check how to improve the filter, this sounds like baaaad, is the flow definition wrong, I know.
    mis_estados = Q(pedidostate = '100') | Q (pedidostate = '12100') | Q(pedidostate = '10000' ) | Q(pedidostate = '20000')
    search_estados = mis_estados & Q ( cliente__user= current_user.id)
    pedidos = Pedidos.objects.filter(search_estados)
    pedidos_estados = {}
    #is ugly, but should make jinja easier
    print current_user.id
    for k in Pedidos.STATE_CHOICES:
      pedidos_estados[str(k[0])]=k[1]
      #here we should decide which state will be an actual acction, like "Reformular Pedido":12100
    print pedidos_estados
    #sort by lista.. and add the staff there 
    pedidos_modales = ''
    print pedidos
    for pedido in pedidos:
      pedidos_modales += generate_modales_encurso(pedido)
      print pedido.pedidostate
    context = {'username': username,
               'current_page': current_page,
               'pedidos': pedidos,
               'pedidos_modales': pedidos_modales,
               'pedidos_estados': pedidos_estados,
               }
    return render(request, 'cliente/encurso_r_pedidos.html',context)

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def update_pedidostate(request,proveedor_id,pedido_ref,transition):
  print "we have something here"
  #TODO: this is duplicated inside helpers_proveeedor, unify and add to settings
  #You cannot user characters like "-_" in here, cause you cannot afford ids MTF
  grouped_by = settings.GROUPED_BY
  current_user = request.user
  username = str(current_user.username)
  cliente = Cliente.objects.get(user_id=current_user.id)
  if request.is_ajax():
    pedido = Pedidos.objects.get(codigo=pedido_ref)
    if str(pedido.proveedor_id) == proveedor_id:
      print "we are sure that the proveedor is the one that should be for this pedido"+proveedor_id
      print "from pedido {0}, from current_user{1} ".format(pedido.cliente.all()[0].id,current_user.id)
      if pedido.cliente.all()[0].id == cliente.id:
        print "we are sure the pedido belongs to the client"
        print "we want to move the pedido "+str(pedido_ref)+ "using:"+str(transition)
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
            'text': 'Tu peticion ha sido procesada',
            '1':'reset'
          }
        pay_load = json.dumps(data)
        return HttpResponse(pay_load, content_type="application/json")
      else:
        print "looks like this pedido do not belong to this user..."
        return HttpResponseRedirect(reverse('pedidos_en_curso'))

    else:
      print "Someone is playing bad.. proabbly"+str(proveedor_id)
      return redirect('/proveedor/404/', request)
  else:
    return HttpResponseRedirect(reverse('pedidos_en_curso'))

@login_required(login_url='/mylogin/')
@user_passes_test(is_cliente)
def retry_pedido_cliente(request,proveedor_id,pedido_ref,transition):
  print "we have an offer"
  current_user = request.user
  username = str(current_user.username)
  proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
  print "requested proveedor"
  print proveedor_id
  msg = ''
  order = ''
  status = 0
  action = 'reload'
  pedido = Pedidos.objects.get(codigo=pedido_ref)
  cliente = Cliente.objects.get(user_id=current_user.id)
  if str(pedido.proveedor_id) == proveedor_id:
    if pedido.cliente.all()[0].id == cliente.id:
      if request.is_ajax():
        update_parameters = request.POST.copy()
        print update_parameters
        if update_parameters:
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
                print "try1"
                producto = Producto.objects.get(product_ref = new_ref, tarifa__id = tarifa.id)
                order['descripcion'][new_ref]= producto.descripcion
                order['precio'][new_ref] = float(producto.precio)
                try:
                  print "try2"
                  order['orden'][new_ref] = float(update_parameters[i])
                except:
                  order['orden'][new_ref] = 1
                order['active'][new_ref] = 1
              except:
                msg += 'Parece que la refencia: '+new_ref+'  No existe asociada a la tarifa '+str(tarifa)+'\n'
          print "Our new order is ready:"
          if order == '':
            msg = 'No has realizado ningun cambio'
            action = ''
            print "wmpty order"
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
              print "to: "+str(pedido.pedidostate)
              print "something tells me there is an extra state here.."
              if t.target == 12200:
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
    else:
      print "Someone is hacking around... "
      return HttpResponse('', content_type="application/json")
  else:
    print "Someone is hacking around... "
    return HttpResponse('', content_type="application/json")

