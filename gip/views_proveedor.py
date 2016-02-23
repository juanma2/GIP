from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test


#import only the needed ones
from gip.models import *

from gip.utils import is_proveedor

@login_required(login_url='/login/')
@user_passes_test(is_proveedor)
def index_proveedor(request):
    my_test_string = 'Vista Proveedor'
    context = {'my_test_string': my_test_string}
    return render(request, 'proveedor/index_proveedor.html', context)

