from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q




#import only the needed ones
from gip.models import *

from gip.utils import is_proveedor

ELEMENTOS_POR_PAGINA_PROVEEDOR = 20
PROVEEDOR_ATTRIBUTE = 'proveedor'

@login_required(login_url='/login/')
@user_passes_test(is_proveedor)
def index_proveedor(request):
    my_test_string = 'Vista Proveedor'
    context = {'my_test_string': my_test_string}
    return render(request, 'proveedor/index_proveedor.html', context)

def productos_proveedor(request):
    #we will retrieve Promo and show per Tarifa/User
    current_user = request.user
    username = str(current_user.username)
    current_page = "Productos"
    proveedor = current_user.groups.all().exclude(name=PROVEEDOR_ATTRIBUTE)[0]
    print proveedor.id
    #get all the categories
    categorias_list = Categoria.objects.all()
    user_listas = Cliente.objects.get(id=current_user.id).listas.all()
    sub_categorias_list = []
    #TODO:filter using disable and filtering by tarifa my friend
    search_parameters = request.POST.copy()
    print search_parameters
    if search_parameters:
      #wipe out the csrf:
      search_parameters.pop('csrfmiddlewaretoken')
      full_search = Q()
      if 'search' in search_parameters:
        print "a provider is searching!!"
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
      all_product_list = Producto.objects.filter(full_search).order_by('-id').values('product_ref').distinct()
      paginator = Paginator(all_product_list, ELEMENTOS_POR_PAGINA_PROVEEDOR)
      if 'page' in search_parameters:
        page = search_parameters['page']
      else:
        page = 1
    else:
      all_product_list = Producto.objects.all().order_by('-id').values('product_ref').distinct()
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
               'user_listas': user_listas,
               'search_parameters': search_parameters
                }

    return render(request, 'proveedor/productos_bootstrap_proveedor.html', context)


