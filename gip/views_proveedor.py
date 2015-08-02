from django.shortcuts import render

#import only the needed ones
from gip.models import *


def index_proveedor(request):
    my_test_string = 'Vista Proveedor'
    context = {'my_test_string': my_test_string}
    return render(request, 'proveedor/index.html', context)

