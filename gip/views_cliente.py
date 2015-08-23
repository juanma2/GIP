from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

#import only the needed ones

from gip.models import *
from gip.utils import is_cliente

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
    print "my client has tarifas"+str(tarifas)
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

