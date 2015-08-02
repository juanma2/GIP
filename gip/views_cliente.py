from django.shortcuts import render

#import only the needed ones

from gip.models import *


def index_cliente(request):
    my_test_string = 'Vista cliente'
    context = {'my_test_string': my_test_string}
    return render(request, 'cliente/index.html', context)

