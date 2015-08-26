from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#import only the needed ones
from gip.models import *
from gip.utils import is_cliente

ELEMENTOS_POR_PAGINA = 8

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
    print promo_list
    context = {'username': username, 
               'current_page': current_page,
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
    all_product_list = Producto.objects.all()
    #this is he default search
    paginator = Paginator(all_product_list, ELEMENTOS_POR_PAGINA)
    page = request.GET.get('page')
    try:
        product_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        product_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        product_list = paginator.page(paginator.num_pages)
    #you need to send a compbo with the current_lists of the user
    context = {'username': username,
               'current_page': current_page,
               'product_list': product_list,
               'categorias_list': categorias_list,
               'sub_categorias_list': sub_categorias_list
		}
               
    return render(request, 'cliente/productos_cliente.html', context)

