from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

#import only the needed ones

from gip.models import *
from gip.utils import is_cliente

@login_required(login_url='/login/')
@user_passes_test(is_cliente)
def index_cliente(request):
    my_test_string = 'Vista cliente'
    context = {'my_test_string': my_test_string}
    return render(request, 'cliente/index_cliente.html', context)

